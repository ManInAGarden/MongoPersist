from types import LambdaType
from MpBase import MpBase

from typing import Dict,List

class MpResolve():

    @classmethod
    def MapName():
        return "MPFACTORY"

    def __init__(self):
        self._autofill = False

    def getfilter(self, me : MpBase):
        raise NotImplementedError("Override MpMapping")

    @property
    def autofill(self):
        return self._autofill

    @autofill.setter
    def autofill(self, value):
        self._autofill = value

class MpListResolve(MpResolve):
    """ Class used to describe how a field ist connected to a mongodb
    """

    @classmethod
    def Map(cls, localFieldName : str ="_id", foreignFieldName : str = None, othercls = None, autofill : bool=False):
        """ Constructs a dictionory for use with dataclass fields to construct metadate

            Parameters
            ----------

            localFieldName : Name of a local field to used for comparison when data are searched

            foreignFieldName : Name of the foreign field to be used for comparision

            othercls : type of other class (must bei a cls)

            autofill : Boolean to mark wether the field will be filled automatically with data when the parent
                       data are fetched from the database (default: False)

            Returns
            -------
            proxydict : a dictionary with just one entry. Key is MPFACTORY and value is an instance of MPResolveList
                        with the data given
        """

        return {MpResolve.MapName: MpListResolve(localFieldName,
                                    foreignFieldName,
                                    othercls,
                                    autofill)}

    def __init__(self, localFieldName, foreignFieldName, othercls, autofill):
        """ Constructor for MpListResolve

            do not use directly. Use classmethode Map(...) instead
        """
        self._localFieldName = localFieldName
        self._foreignFieldName = foreignFieldName
        self._othercls = othercls
        self._autofill = autofill

    def getfilter(self, me : MpBase) -> Dict[str,object]:
        """ Get the filter dict to be used with Mongo_db finds

            Paramaters
            ----------

            me : the parent class, already filled with data. me must be derived from MpBase

            Returns
            -------
            A dictionary to be used in pymongo find - calls
        """

        if self._foreignFieldName is None:
            raise Exception("No foreignFieldFound in <" + self.__class__.__name + ">")

        localdata = getattr(me, self._localFieldName)
        foreigname = self._foreignFieldName

        filt = {foreigname : localdata}

        return filt

    @property
    def otherclass(self):
        return self._othercls

class MpSingleResolve(MpResolve):
    @classmethod
    def Map(cls, localFieldName : str = None, foreignFieldName : str = "_id", othercls = None, autofill : bool=False):
        """ Constructs a dictionory for use with dataclass fields to construct metadate

            Parameters
            ----------

            localFieldName : Name of a local field to used for comparison when data are searched

            foreignFieldName : Name of the foreign field to be used for comparision

            othercls : type of other class (must bei a cls)

            autofill : Boolean to mark wether the field will be filled automatically with data when the parent
                       data are fetched from the database (default: False)

            Returns
            -------
            proxydict : a dictionary with just one entry. Key is MPFACTORY and value is an instance of MPResolveList
                        with the data given
        """

        return {MpResolve.MapName: MpSingleResolve(localFieldName,
                                    foreignFieldName,
                                    othercls,
                                    autofill)}

    def __init__(self, localFieldName, foreignFieldName, othercls, autofill):
        """ Constructor for MpListResolve

            do not use directly. Use classmethode Map(...) instead
        """
        self._localFieldName = localFieldName
        self._foreignFieldName = foreignFieldName
        self._othercls = othercls
        self._autofill = autofill

    @property
    def otherclass(self):
        return self._othercls

    def getfilter(self, me : MpBase) -> Dict[str,object]:
        """ Get the filter dict to be used with Mongo_db finds

            Paramaters
            ----------

            me : the parent class, already filled with data. me must be derived from MpBase

            Returns
            -------
            A dictionary to be used in pymongo find - calls
        """

        if self._foreignFieldName is None:
            raise Exception("No foreignFieldFound in <" + self.__class__.__name + ">")

        localdata = getattr(me, self._localFieldName)
        foreigname = self._foreignFieldName

        filt = {foreigname : localdata}

        return filt
        

    
