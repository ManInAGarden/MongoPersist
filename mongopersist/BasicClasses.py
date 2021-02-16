import datetime as dt
import uuid
import inspect

from pymongo.common import RETRY_READS

class ClassDictEntry(object):
    def __init__(self, membername, dectype, declaration):
        self._membername = membername
        self._dectype = dectype
        self._declaration = declaration

    def  get_default(self):
        return self._declaration.get_default()

    def get_dectype(self):
        return self._dectype

    def get_declaration(self):
        return self._declaration

    def __repr__(self):
        return "datamember: {} dectype{} declared {}".format(self._membername, self._dectype, self._declaration)

class BaseType(object):
    _innertype = None
    _subclasses = []
    _myfieldname = None #used to cache a field name once it was searched by get_fieldname()

    def __init__(self, **kwarg):
        self._varcode = uuid.uuid4()
        self._getpara(kwarg, "default")
        self._getpara(kwarg, "defaultgenerator")
        
    def get_default(self):
        if self._defaultgenerator is None:
            return self._default
        else:
            return self._defaultgenerator()

    def to_innertype(self, dta):
        raise Exception("Override me in <BaseType.to_innertype() in declration-type {}".format(type(self).__name__))

    def get_fieldname(self):
        if self._myfieldname is not None: return self._myfieldname

        vname = getvarname(self)
        self._myfieldname = vname
        return vname

    def _getpara(self, kwargs, name, default=None, excstr=None):
        membername = "_" + name
        done = False
        if name in kwargs.keys():
            setattr(self, membername, kwargs[name])
            done = True
        elif default is not None:
            setattr(self, membername, default)
            done = True
        elif excstr is not None:
            done = True
            raise Exception(excstr)

        if not done:
            setattr(self, membername, None)

class String(BaseType):
    _innertype = str
    def __init__(self, **kwarg):
        super().__init__(**kwarg)

    def to_innertype(self, dta):
        if dta is None:
            return None
        else:
            return str(dta)
        

class UUid(BaseType):
    _innertype = uuid.uuid4

    def to_innertype(self, dta):
        if dta is None:
            return None
        t = type(dta)

        if t is uuid.uuid4:
            return dta
        elif t is str:
            return uuid.UUID(dta)
        else:
            raise Exception("Type <{0}> cannot be tranformed into a uuid".format(t.__name__))

class Int(BaseType):
    _innertype = int

    def to_innertype(self, dta):
        if dta is None:
            return None
        t = type(dta)

        if t is int:
            return dta
        elif t is str:
            return int(dta)
        else:
            raise Exception("Type <{0}> cannot be tranformed into an int".format(t.__name__))

class Float(BaseType):
    _innertype = float

    def to_innertype(self, dta):
        if dta is None:
            return None
        t = type(dta)

        if t is float:
            return dta
        elif t is str:
            return float(dta)
        else:
            raise Exception("Type <{0}> cannot be tranformed into a float".format(t.__name__))

class DateTime(BaseType):
    innertype = dt.datetime

    def to_innertype(self, dta):
        if dta is None:
            return None
        t = type(dta)

        if t is dt.datetime:
            return dta
        elif t is str:
            return dt.strptime(dta, "%m.%d.%Y %H:%M:%S")
        else:
            raise Exception("Type <{0}> cannot be tranformed into a uuid".format(t.__name__))

class Catalog(BaseType):
    _innertype = str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._getpara(kwargs, "catalogtype", excstr="catalogdefinition without catalogtype is not a valid catalog definition")

    def to_innertype(self, dta):
        raise Exception("do not use to_innertype in catalogs!")

    def get_catalogtype(self):
        return self._catalogtype


class EmbeddedObject(BaseType):
    _innertype = object

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._getpara(kwargs, "targettype", excstr="EmbeddedObject needs a targettype!!")
        self._getpara(kwargs, "autofill", default=True)

    def get_targettype(self):
        return self._targettype

    def get_autofill(self) -> bool:
        return self._autofill

    def get_foreign_keyname(self):
        if type(self._foreignid) is str: return self._foreignid

        vname = getvarname(self._foreignid)

        if vname is not None: #if we managed to get the name, store it for future use (caching)
            self._foreignid = vname

        return vname

    def get_local_keyname(self):
        if type(self._localid) is str: return self._localid

        vname = getvarname(self._localid)

        if vname is not None: #if we managed to get the name, store it for future use (caching)
            self._localid = vname

        return vname


class EmbeddedList(EmbeddedObject):
    _innertype = list

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class JoinedEmbeddedList(EmbeddedList):
    _innertype = list

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._getpara(kwargs, "localid", default="_id")
        self._getpara(kwargs, "foreignid", excstr="A JoinedEmbeddedList needs a foreign id!!!")
        self._getpara(kwargs, "autofill", default=False)
        self._getpara(kwargs, "cascadedelete", default=False)

    def get_cascadedelete(self):
        return self._cascadedelete


class IntersectedList(EmbeddedList):
    _innertype = list

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._getpara(kwargs, "autofill", default=False)

class JoinedEmbeddedObject(EmbeddedObject):
    _innertype = object

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._getpara(kwargs, "localid", excstr="A JoinedEmbeddedObject needs a local id which points to the joined object")
        self._getpara(kwargs, "foreignid", default="_id")
        self._getpara(kwargs, "cascadedelete", default=False)

    def get_cascadedelete(self):
        return self._cascadedelete

class MpBase(object):
    _classdict = {}
    Id = String() #convention use uppercase first letter to create a correct data definition!!!!!! 
    Created = DateTime() # see - upercase name!!!!
    Lastupdate = DateTime() # same here

    @classmethod
    def _setup_class_dict(cls):

        if cls in cls._classdict.keys(): return

        classmemberdict = {}
        allclasses = inspect.getmro(cls)
        for allclass in allclasses:
            if issubclass(allclass, MpBase):
                members = vars(allclass)
                for key, value in members.items():
                    if key[0].isupper() and issubclass(value.__class__, BaseType):
                        if key=="Id":
                            mykey = "_id"
                        else:
                            mykey = key.lower()

                        classmemberdict[mykey] = ClassDictEntry(key, value, getattr(allclass, key))
        
        cls._classdict[cls] = classmemberdict

    @classmethod
    def get_collection_name(cls):
        if hasattr(cls, "_collectionname"):
            return getattr(cls, "_collectionname")
        else:
            return cls.__name__


    def __init__(self, **kwargs):
        self._valuesdict = {}
        self.__class__._setup_class_dict()
        for key, value in kwargs.items():
            self._set_my_attribute(key, value)
        self.initialise_attributes()

    def initialise_attributes(self):
        vd = self._get_my_memberdict()
        for key, value in vd.items():
            if hasattr(self, key) and getattr(self, key) is not None:
                continue
            
            setattr(self, key, value.get_default())

    def _set_my_attribute(self, key, value):
        """ set my own attributes in a controlled manner
        """
        mycld = self._get_my_memberdict()
        if key not in mycld.keys():
            raise Exception("Cannot initialise undefined member {}".format(key))

        setattr(self, key, value)
        
    def _get_my_memberdict(self):
        mycls = self.__class__
        return mycls._classdict[mycls]

    def get_memberdeclaration(self, membername):
        md = self._get_my_memberdict()[membername]
        return md.get_declaration()

class MpCatalog(MpBase):
    _collectionname = "catalog"
    Type = String()
    Code = String()
    Value = String()
    LangCode = String()

def getvarname(decl: BaseType):
    """get the name used for a field of a declaration 

       search is done by _varcode which every intstance of a field declaration gets automatically
    """
    for cls, cldentry in MpBase._classdict.items():
        for key, value in cldentry.items():
            if value._declaration._varcode == decl._varcode: 
                return key

    return None