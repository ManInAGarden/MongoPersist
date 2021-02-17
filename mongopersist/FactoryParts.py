from mongopersist.BasicClasses import BaseType, Catalog, ClassDictEntry, EmbeddedList, EmbeddedObject, JoinedEmbeddedList, JoinedEmbeddedObject, MpBase, MpCatalog, OperationStackElement, OrderInfo, String, Val, getvarname
import pymongo as pym
from bson import codec_options
import datetime as dt
from uuid import uuid4


class MpFactory(object):

    def __init__(self, url, subname):
        self._mongoclient = pym.MongoClient(url)
        self._db = self._mongoclient[subname]
        self._lang = "GBR"
        self._catcache = {}

    @property
    def get_db(self):
        return self._db

    def cat(self, cls, code : str) -> MpCatalog:
        """creates a new MpCatalog entry searched from the db by ist code
        """

        if code is None: return None

        if not issubclass(cls, MpCatalog):
            raise Exception("<{}> is not a subclass of a MpCatalog".format(cls.__name__))

        if not hasattr(cls, "_cattype"):
            raise Exception("<{}> is not a valid catalog because _cattype class member is missing.".format(cls.__name__))

        cachekey = cls._cattype + "#" + self._lang + "#" + code
        if cachekey in self._catcache.keys():
            return self._catcache[cachekey]

        srchdict = {"langcode":self._lang, "type":cls._cattype, "code":code}
        res = self.find(cls, srchdict)

        if res is None or len(res) != 1:
            raise Exception("Not exactly one entry for code <{}>, type <{}>, language <{}> could be found in cat colllection <{}>".format(code, 
                    cls._cattype, 
                    self._lang, 
                    cls.get_collection_name()))

        catentry = res[0]
        self._catcache[cachekey] = catentry

        return catentry


    def flush(self, dco : MpBase) -> None:
        """Store the contents of an instance of a Mpbase derived class into it's document

            Paramaters
            ----------

            dco : An instance of a class which is derived from MpBase
        """
        ts = dt.datetime.now()
        if dco._id is None:
            dco.created = ts
            dco.lastupdate = ts
        else:
            dco.lastupdate = ts

        dcodict = self._get_mongodict(dco)

        t = type(dco)
        colname = dco.__class__.get_collection_name()
        col = self._db.get_collection(colname)

        if dcodict["_id"] is None:
            dcodict["_id"] = uuid4().hex
            id = col.insert_one(dcodict)
            dco._id = id.inserted_id
        else:
            dcodict.pop("_id") # we do not change the id, nor do we change Created
            dcodict.pop("created")
            col.update_one({"_id" : dco._id}, {"$set" : dcodict})

    def _get_mongodict(self, dco : MpBase) -> dict:
        mongdict = {}
        membdict = dco._get_my_memberdict()
        for membkey, membval in membdict.items():
            mongdict[membkey] = self._get_value(membval, getattr(dco, membkey))

        return mongdict

    def _get_value(self, clsentry : ClassDictEntry, rawvalue):
        if rawvalue is None:
            return rawvalue

        decl = clsentry.get_declaration()
        t = type(decl)
        if t is Catalog:
            return rawvalue.code
        elif t is EmbeddedObject:
            return self._get_mongodict(rawvalue)
        elif t is EmbeddedList:
            targt = decl.get_targettype()
            return self._get_mongo_dictlist(targt, rawvalue)
        else:
            return rawvalue

    def _get_mongo_dictlist(self, targettype, val) -> list:
        answ = []

        for singleval in val:
            if issubclass(targettype, MpBase):
                answ.append(self._get_mongodict(singleval))
            else:
                answ.append(singleval)

        return answ

    def delete(self, dco):
        with self._mongoclient.start_session() as sess:
            with sess.start_transaction() as trans:
                self._notransdeletecascaded(dco)

    def _notransdeletecascaded(self, dco):
        t = type(dco)

        if not issubclass(t, MpBase):
            raise Exception("Type <{}> is not supported in MpFactory.delete()".format(t.__name__))

        if dco._id is None: raise BaseException("No delete withoud an _id!")

        membdict = dco._get_my_memberdict()
        for membkey, membval in membdict.items():
            decl = membval._declaration
            declt = type(decl)
            if issubclass(declt, JoinedEmbeddedObject) and decl.get_cascadedelete():
                self.resolve(dco, membkey)
                loco = getattr(dco, membkey)
                if not loco is None:
                    self._notransdeletecascaded(loco)

            elif issubclass(declt, JoinedEmbeddedList) and decl.get_cascadedelete():
                self.resolve(dco, membkey)
                locos = getattr(dco, membkey)
                for loco in locos:
                    self._notransdeletecascaded(loco)

        self._notransdelete(dco)



    def _notransdelete(self, dco):
        """Delete a data object from its collection 

            dco : The data object to be deleted (_id has to be filled!)
        """

        t = type(dco)

        if not issubclass(t, MpBase):
            raise Exception("Type <{}> is not supported in MpFactory.delete()".format(t.__name__))

        if dco._id is None: raise BaseException("No delete withoud an _id!")
        
        delcls = type(dco)
        colname = delcls.get_collection_name()
        col = self._db.get_collection(colname)
        delres = col.delete_one({"_id" : dco._id})


    def find(self, cls, findpar = None, orderlist=None, limit=0):
        if findpar is None:
            return self.find_with_dict(cls, {}, orderlist, limit)
        elif type(findpar) is dict:
            return self.find_with_dict(cls, findpar,  orderlist, limit)
        elif issubclass(type(findpar), MpBase):
            if findpar._id is None:
                raise Exception("MpFactory.find() with an Mpbase derived instance only works when this instance contains an _id")

            res = self.find_with_dict(cls, {"_id": findpar._id})
            return self._first_or_default(res)
        elif findpar is str:
            res = self.find_with_dict(cls, {"_id": findpar})
            return self._first_or_default(res)
        else:
            raise NotImplementedError("Unsupported type <{}> in findpar.".format(type(findpar)))

    def _first_or_default(self, inl, default=None):
        if inl is None: return default
        if len(inl) <= 0: return default
        return inl[0]

    def find_with_dict(self, cls, filterdict : dict, orderlist=None, limit=0) -> list:
        colname = cls.get_collection_name()
        col = self._db.get_collection(colname)

        if orderlist is None or len(orderlist) <= 0:
            dcodict = col.find(filterdict, limit = limit)
        else:
            dcodict = col.find(filterdict, limit = limit).sort(orderlist)

        answ = []
        if dcodict is not None:
            for element in dcodict:
                dco = self._create_inst(cls, element)
                answ.append(dco)
                
        return answ

    def _create_inst(self, cls, dtadict : dict) -> MpBase:
        if dtadict is None: return None

        answ = cls()

        #1. without linked embeddeds because foreign keys might not yet be filled
        for key, dat in dtadict.items():
            decl = answ.get_memberdeclaration(key)
            declt = type(decl)
            if issubclass(declt, Catalog):
                setattr(answ, key, self.get_cat_value(decl, dat))
            elif declt is EmbeddedObject:
                tgt = decl.get_targettype()
                setattr(answ, key, self._create_inst(tgt, dat))
            elif declt is EmbeddedList:
                setattr(answ, key, self.get_embeddedlist(decl, dat))
            elif declt is JoinedEmbeddedObject:
                pass
            elif declt is JoinedEmbeddedList:
                pass
            else:
                setattr(answ, key, decl.to_innertype(dat))

        #2 now foreign keys should all have data
        for key, dat in dtadict.items():
            decl = answ.get_memberdeclaration(key)
            declt = type(decl)
            if declt is JoinedEmbeddedObject:
                if getattr(answ, key) is None: #only do this once
                    setattr(answ, key, self.get_joined_embeddedobject(decl, answ))
            elif declt is JoinedEmbeddedList:
                if getattr(answ, key) is None: #only do this once
                    setattr(answ, key, self.get_joined_embeddedlist(decl, answ))

        return answ

    def get_joined_embeddedlist(self, decl : JoinedEmbeddedObject, parent : MpBase, inresolve=False) -> MpBase:
        if parent is None:
            raise Exception("None parent in get_joined_embeddedlist()")

        af = decl.get_autofill()

        if not (af or inresolve):
            return None

        tgty = decl.get_targettype()
        foreignkeyname = decl.get_foreign_keyname()
        localkeyname = decl.get_local_keyname()
        localkey = getattr(parent, localkeyname)
        srchdict = {foreignkeyname : localkey}
        res = self.find(tgty, srchdict)

        return res


    def get_joined_embeddedobject(self, decl : JoinedEmbeddedObject, parent : MpBase, inresolve=False) -> MpBase:
        if parent is None:
            raise Exception("None parent in get_joined_embeddedobject()")

        af = decl.get_autofill()

        if not (af or inresolve):
            return None

        tgty = decl.get_targettype()
        foreignkeyname = decl.get_foreign_keyname()
        localkeyname = decl.get_local_keyname()
        localkey = getattr(parent, localkeyname)
        srchdict = {foreignkeyname : localkey}
        res = self.find(tgty, srchdict)

        if res is None or len(res)!=1:
            raise Exception("Not exactly one foreign object found in get_joined_embeddedobject while searching class <{}> with dict <{}>".format(
                                                        tgty, srchdict))

        return res[0]

    def get_embeddedlist(self, decl, data):
        if data is None: return None
        #we expect data to be a list
        answ = []
        tgty = decl.get_targettype()
        for dat in data:
            daty = type(dat)
            if daty is tgty:
                answ.append(dat)
            elif daty is dict:
                answ.append(self._create_inst(tgty, dat))
            else:
                raise Exception("Do not now how to handle an embedded list element of type <{0}> in get_embeddedlist".format(daty.__name__))

        return answ

    def get_cat_value(self, decl, data):
        if data is None:
            return None

        catcls = decl.get_catalogtype()
        return self.cat(catcls, data)

    def resolve(self, dco, *fields):
        for targfield in fields:
            t = type(targfield)
            if t is str:
                fieldname = targfield
                fieldecl = dco.get_memberdeclaration(fieldname)
                self._resolve_for(dco, targfield, fieldecl)
            elif issubclass(t, BaseType):
                fieldname = targfield.get_fieldname()
                fielddecl = targfield
                self._resolve_for(dco, fieldname, fielddecl)
            else:
                raise Exception("Unsupported field type <{}> in MpFactory.resolve ".format(t.__name__))

    def _resolve_for(self, dco, fieldname, fielddecl):
        if getattr(dco, fieldname) is not None: return

        t = type(fielddecl)
        if t is JoinedEmbeddedList:
            setattr(dco, fieldname, self.get_joined_embeddedlist(fielddecl, dco, inresolve=True))
        elif t is JoinedEmbeddedObject:
            setattr(dco, fieldname, self.get_joined_embeddedobject(fielddecl, dco, inresolve=True))
        else:
            raise Exception("<{}> is not a resolvable field".format(fieldname))

    
class MpQueryIterator(object):
    def __init__(self, mpq):
        self._mpq = mpq
        self._datalist = None
        self._index = 0

    def __next__(self):
        if self._datalist is None:
            self._datalist = self._mpq.finddata()
        
        if self._index >= len(self._datalist):
            raise StopIteration

        nextv = self._datalist[self._index]
        self._index += 1
        return nextv

    def first_or_default(self, default):
        """get first element of the iteration or a default value when nothing can be found

           When no result can be found the default is returned
           instead.

           parameters
           ----------

           default: a default which will be returned instead of raising an exception in case no
           results can be found

           Returns
           -------

           The first element of the query result
        """

        if self._datalist is None:
            self._datalist = self._mpq.finddata()

        if len(self._datalist) <= 0:
                return default

        return self._datalist[0]

    def first(self):
        """get first element of the iterator

           When no result can be found an exception is raised

           Returns
           -------

           The first element of the query result
        """
        if self._datalist is None:
            self._datalist = self._mpq.finddata()

        if len(self._datalist) <= 0:
            raise Exception("No results where found")

        return self._datalist[0]

class MpQuery(object):
    opmapping = {"==":"$eq", 
            "!=":"$neq",
            ">":"$gt",
            "<":"$lt",
            ">=":"$gte",
            "<=":"$lte"}
    logmapping = {"&":"$and",
            "|":"$or"}

    def __init__(self, fact : MpFactory, cls : MpBase):
        self._mpf = fact
        self._cls = cls
        self._whereop = None
        self._order = None

    def where(self, express = None):
        self._whereop = express
        return self

    def first_or_default(self, default):
        """get first element of the query result

           When no result can be foudn the default is returned
           instead.

           parameters
           ----------

           default: a default which will be returned instead of raising an exception in case no
           results can be found

           Returns
           -------

           The first element of the query result
        """
        it = iter(self)
        return it.first_or_default(default)

    def first(self):
        """get first element of the query result

           When no result can be found an exception is raised

           Returns
           -------

           The first element of the query result
        """
        it = iter(self)
        return it.first()

    def order_by(self, *args):
        self._order = []

        for arg in args:
            tolm = type(arg)

            if issubclass(tolm, BaseType):
                oi = OrderInfo(arg, "asc")
            elif tolm is OrderInfo:
                oi = arg

            self._order.append(oi)

        return self

    def finddata(self):
        qdict, orderlist = self._generateall()
        return self._mpf.find(self._cls, qdict, orderlist)

    def _generateall(self):
        qdict = self._getquerydict(self._whereop)
        orderl = self._generateorderlist(self._order)
        return qdict, orderl

    def _generateorderlist(self, ol):
        if ol is None: return None
        if len(ol) <= 0: return None

        answ = []
        for olm in ol:
            answ.append(self._getorder(olm))

        return answ

    def _getorder(self, olm):
        field = olm.field
        if olm.orderdir == "asc":
            dir = pym.ASCENDING
        elif olm.orderdir == "desc":
            dir = pym.DESCENDING
        else:
            raise Exception("Unknown ordering direction <{}> in _getorder()".format(olm._order))

        fieldname = getvarname(field)
        return (fieldname, dir)

        

    def _getquerydict(self, op):
        if op is None:
            return {} #no query supplied -> query all

        leftpart = self._getpart(op._left)
        rightpart = self._getpart(op._right)
        oppart = self._getop(op._op)

        if oppart in ["$and", "$or"]:
            return {oppart:[leftpart, rightpart]}
        elif oppart in self.opmapping.values():
            return {leftpart:{oppart: rightpart}}
        else:
            raise Exception("Uuuuuups in _getquerydict")
        
    def _getop(self, op):
        mapping = {**self.opmapping, **self.logmapping} #merge mappings
        
        if not op in mapping.keys():
            raise Exception("Unknown operator <{}>".format(op))

        return mapping[op]

    def _getpart(self, part):
        t = type(part)
        if t is OperationStackElement:
            part = self._getquerydict(part)
        elif issubclass(t, BaseType):
            part = getvarname(part)
        elif t is Val:
            part = part._value

        return part

    def __iter__(self):
       ''' Returns the Iterator object '''
       return MpQueryIterator(self)