from dataclasses import dataclass
from typing import ClassVar, TypeVar, Generic
import datetime as dt


@dataclass(init=False)
class MpBase():
    _id : str = None
    created : dt.datetime = None
    lastupdate : dt.datetime = None

    @classmethod
    def CollectionName(cls):
        """ Returns the collection name to be used in the database. Default is to return the name of the class as a collection name

            override this class Method in your class if you need a collection name not equal to the class name
        """
        return cls.__name__

@dataclass(init=False)
class SimpleCatalogue(MpBase):
    languagecode : str = None
    code : str = None
    value : str = None

    def CatInit(self, lcode, code, val):
        self._id = None
        self.languagecode = lcode
        self.code = code
        self.value = val

        return self

@dataclass(init=False)
class MpIntersectBase(MpBase):
    parentid : str = None #id pointing to the parent class of this intersection
    targetid : str = None #id pointing to the target of this intersection
