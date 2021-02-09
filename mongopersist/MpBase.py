from dataclasses import dataclass
from typing import ClassVar, TypeVar, Generic
import datetime as dt

class Noneable():
    def __init__(self, val) -> None:
        self.__value = val

    def hasvalue(self) -> bool:
        if self.__value is not None:
            return True
        else:
            return False

    def getvalue(self):
        return self.__value

    value = property(getvalue)

class NoneableDateTime(Noneable):
    pass

class NoneableBool(Noneable):
    pass

@dataclass(init=False)
class MpBase():
    _id : str = None
    created : NoneableDateTime = None
    lastUpdate : NoneableDateTime = None

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
