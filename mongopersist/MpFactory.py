from .MpDecorators import MpListResolve, MpResolve, MpSingleResolve
import typing
from .MpBase import MpBase, Noneable, NoneableDateTime, SimpleCatalogue
from uuid import uuid4
from bson import codec_options
import pymongo as pym
import dataclasses as dc
from pymongo.message import update
import datetime as dt
import importlib
from dataclasses import dataclass, is_dataclass

class MpFactory():
    def __init__(self, url, subname):
        self._seeds_done=[]
        self.mongoclient = pym.MongoClient(url)
        self.db = self.mongoclient[subname]
        self.lang = "GBR"
        self.catcache = {}

    def initseeddata(self, cls):
        if not is_dataclass(cls):
            raise Exception("Class <{0}> is no dataclass. Function initseeddata is only valid for dataclasses.".format(cls))

        if cls.__name__ in self._seeds_done:
            return

        colname = cls.CollectionName()
        self.db.drop_collection(colname)
        seeds = cls.GetSeedData()
        for seed in seeds:
            self.flush(seed)
        
        self._seeds_done.append(cls.__name__)

    def flush(self, dco):
        if not dc.is_dataclass(dco) : raise BaseException("Keine Datenklasse in Flush!")

        ts = NoneableDateTime(dt.datetime.now())
        if dco._id is None:
            dco.created = ts
            dco.lastupdate = ts
        else:
            dco.lastupdate = ts

        #dcodict = dc.asdict(dco) können wir nicht nehmen weil es rekursiv arbeitet. s. Sonderbehandlung in GetMongodict()
        dcodict = self.getmongodict(dco)

        t = type(dco)
        colname = dco.__class__.CollectionName()
        col = self.db.get_collection(colname)

        if dcodict["_id"] is None:
            dcodict["_id"] = uuid4().hex
            id = col.insert_one(dcodict)
            dco._id = id.inserted_id
        else:
            dcodict.pop("_id") # we do not change the id, nor do we change Created
            dcodict.pop("created")
            col.update_one({"_id" : dco._id}, {"$set" : dcodict})

    def getmongodict(self, dco):
        answdict = {}
        fields = dc.fields(dco)
        try:
            for field in fields:
                fn = field.name
                try:
                    val = getattr(dco, fn)
                except:
                    val = None

                if dc.is_dataclass(field.type):
                    if issubclass(field.type, SimpleCatalogue):
                        if val is None:
                            answdict[fn] = None
                        else:
                            answdict[fn] = {"###MPCATCLASS###" : field.type.__module__ + "." + field.type.__name__,
                                    "code" : val.code}
                    elif self.issingleresolveable(field):
                        pass #do not add to the dict because data will be fetched via resolve
                    else:
                        if val is None:
                            answdict[fn] = None
                        else:
                            answdict[fn] = self.getmongodict(val)
                            answdict[fn]["###MPCLASS###"] = field.type.__module__ + "." + field.type.__name__

                elif hasattr(field.type, "_name") and field.type._name in ("List","Set"):
                    innercl = field.type.__args__
                    if self.islistresolveable(field):
                        pass
                    else:
                        answdict[fn] = val #we have a non dataclass embedded here.

                elif issubclass(field.type, Noneable):
                    if val is None:
                        answdict[fn] = None
                    else:
                        answdict[fn] = {"###MPNONEABLE###" : field.type.__module__ + "." + field.type.__name__,
                            "value" : val.value}
                else:
                    answdict[fn] = val

        except Exception as exc:
            raise exc

        return answdict

    def islistresolveable(self, field) -> bool:
        """ test if the field is marked to me list resolved in it's metadata

            Resolving is used for embedded dataclass objects which are not directly 
            embedded into the mongodb document. Instead of embedding the data are
            filled in later on by calling resolve for the fieldname. Then the data
            are fetched from another document and filled into the list resolvaeable
            field. 
            Alternatively a fiel dca be marked as list resolveable with autofill=True.
            The the data are retrieved from another document when the parent object 
            itself is fetched form the database.

            Parameters
            ----------

            field: the field information as defined in the dataclasses property

            Returns:
            True when we have a field marked to be lsit resolveable, False otherwise
        """

        answ = False
        if field.metadata is None:
            return answ
            
        if MpResolve.MapName not in field.metadata:
            return answ

        mpres = field.metadata[MpResolve.MapName]

        answ = type(mpres) is MpListResolve

        return answ


    def issingleresolveable(self, field) -> bool:
        """ test if the field is marked to me single resolved in it's metadata

            Parameters
            ----------

            field: the field information as defined in the dataclasses property

            Returns:
            True when we have a field marked to be single resolved, False otherwise
        """

        answ = False
        if field.metadata is None:
            return answ
            
        if MpResolve.MapName not in field.metadata:
            return answ

        mpres = field.metadata[MpResolve.MapName]

        answ = type(mpres) is MpSingleResolve

        return answ


    def findbyid(self, cls, id):
        dco = None
        colname = cls.CollectionName()
        col = self.db.get_collection(colname)
        dcodict = col.find_one({"_id": id})
        
        if dcodict is not None:
            dco = self.createinstance(cls, dcodict)

        return dco

    def createinstance(self, cls, dcodict):
        dco = cls()
        for name, value in dcodict.items():
            if name=="###MPCLASS###": continue
            if type(value) is dict:
                if "###MPCLASS###" in value.keys(): #wir haben ein dict mit Typ-Info
                    subcls = self.getclass(value["###MPCLASS###"])
                    setattr(dco, name, self.createinstance(subcls, value))
                elif "###MPCATCLASS###" in value.keys(): #wir haben es mit einem Katalogverweis zu tun
                    subcls = self.getclass(value["###MPCATCLASS###"])
                    setattr(dco, name, self.cat(subcls, value["code"]))
                elif "###MPNONEABLE###" in value.keys(): #Wir haben einen Noneable typen
                    subcls = self.getclass(value["###MPNONEABLE###"])
                    nullo = subcls(value["value"])
                    setattr(dco, name, nullo)
                else: #wir haben ein normales dict
                    setattr(dco, name, value)
            else:
                setattr(dco, name, value)

        dco = self.doautofills(dco)

        self.addnonefields(dco) #add missing defaults not retrieved from the db

        return dco

    def addnonefields(self, dco) -> None:
        """ add any missing field (declared in the dataclass but not found in the db) as None values
            or as their declared default values
        """

        if not dc.is_dataclass(dco): #only do this to dataclasses
            return

        for field in dc.fields(dco):
            if not hasattr(dco, field.name):
                if field.default_factory is None:
                    setattr(dco, field.name, field.default)
                else:
                    setattr(dco, field.name, field.default_factory())

    def doautofills(self, dco : MpBase) -> MpBase:
        """ Fills any field marked for for autofill with its data

            Parameters
            ----------

            dco : an instance of an MpBase derived class already filled with any directly available data
        """

        dcoansw = dco

        for field in dc.fields(dco):
            if field.metadata is None:
                continue
            
            if MpResolve.MapName not in field.metadata:
                continue

            mpres = field.metadata[MpResolve.MapName]

            #do we have to resolve something and autofill it
            if issubclass(type(mpres), MpResolve) and mpres.autofill:
                dcoansw = self.dofieldautofill(dco, field)

        return dcoansw

    def dofieldautofill(self, dco : MpBase, field : dc.Field) -> MpBase:
        mpres = field.metadata[MpResolve.MapName]

        if issubclass(type(mpres), MpListResolve):
            setattr(dco, field.name, self.listresolve(dco, field))
        elif issubclass(type(mpres), MpSingleResolve):
            raise NotImplementedError("Autofill for Singleresolve not yet supported")

        return dco
        
    def listresolve(self, dco : MpBase, field : dc.Field) -> typing.List[MpBase]:
        mpres : MpListResolve = field.metadata[MpResolve.MapName]
        filter = mpres.getfilter(dco)
        return self.find(mpres.otherclass, filter)

    def singleresolve(self, dco : MpBase, field : dc.Field) -> MpBase:
        mpres : MpListResolve = field.metadata[MpResolve.MapName]
        filter = mpres.getfilter(dco)
        return self.find_one(mpres.otherclass, filter)

    def resolve(self, dco, *args):
        """ resolve embedded lists and single embedded objects

            Parameters
            ----------

            dco: data object whos properties shall be resolved

            *args: parameter list of names (str) of the properties to be resolved/filled
        """

        fields = dc.fields(dco)
        for arg in args:
            fld = self.getfield(fields, arg)
            if fld is None:
                raise Exception("<{}> exisitiert nicht als Feld in <{}>".format(arg, dco.__class__.__name__))

            mpres = fld.metadata[MpResolve.MapName]

            if issubclass(type(mpres), MpListResolve):
                if not hasattr(dco, fld.name) or getattr(dco, fld.name) is None:
                    setattr(dco, fld.name, self.listresolve(dco, fld))
            elif issubclass(type(mpres), MpSingleResolve):
                if not hasattr(dco, fld.name) or getattr(dco, fld.name) is None:
                    setattr(dco, fld.name, self.singleresolve(dco, fld))

    def getfield(self, fields, fieldname):
        for field in fields:
            if field.name == fieldname:
                return field
        
        return None



    def getclass(self, clsname):
        if clsname is None or len(clsname)==0:
            raise Exception("MpDactory.getclass(classname) for an emty classname is not a valid call")

        lastdot = clsname.rindex('.')
        modulename = clsname[0:lastdot]
        clsname = clsname[lastdot + 1::]
        module = importlib.import_module(modulename)
        return getattr(module, clsname)

    def find(self, cls, findpar = None, limit=0):
        if findpar is None:
            return self.find_with_dict(cls, {}, limit)
        elif type(findpar) is dict:
            return self.find_with_dict(cls, findpar, limit)
        elif issubclass(type(findpar), MpBase):
            if findpar._id is None:
                raise Exception("MpFactory.find() with an Mpbase derived instance only works when this instance contains an _id")

            return self.find_with_dict(cls, {"_id": findpar._id})
        elif findpar is str:
            return self.find_with_dict(cls, {"_id": findpar})
        else:
            raise NotImplementedError("Unsupported type <{}> in findpar.".format(type(findpar)))

    def find_with_dict(self, cls, filterdict : dict, limit=0):
        colname = cls.CollectionName()
        col = self.db.get_collection(colname)
        dcodict = col.find(filterdict, limit = limit)

        answ = []
        if dcodict is not None:
            for element in dcodict:
                dco = self.createinstance(cls, element)
                answ.append(dco)
                
        return answ

    def find_one(self, cls, filterdict):
        answ = None
        colname = cls.CollectionName()
        col = self.db.get_collection(colname)
        dcodict = col.find_one(filterdict)

        if dcodict is not None:
            answ = self.createinstance(cls, dcodict)
        return answ

    def delete(self, dco):
        if dco._id is None: raise BaseException("Kein Löschen ohne _id!")
        colname = dco.__class__.CollectionName()
        col = self.db.get_collection(colname)
        delres = col.delete_one({"_id" : dco._id})

        if delres.deleted_count != 1: raise BaseException("Es wurde nicht exakt ein Dokument gelöscht für Löschen mit _id <" + str(dco._id) + ">")

    def delete_many(self, cls, filter):
        colname = cls.CollectionName()
        col = self.db.get_collection(colname)
        return col.delete_many(filter)

    def cat(self, cls, code):
        cachekey = cls.__name__ + "#" + code

        if cachekey in self.catcache.keys():
            return self.catcache[cachekey]

        res = self.find(cls, {"code":code, "languagecode":self.lang})

        if len(res)==1:
            self.catcache[cachekey] = res[0]
        else:
            raise Exception("Der Katalogeintrag <" + code + "> konnte für die Sprache <" + self.lang + "> und den Katalog <" + cls.__name__ + "> nicht EINDEUTIG gefunden werden.")

        return res[0]




