from types import LambdaType
import pymongo as pym
from bson.objectid import ObjectId
from dataclasses import dataclass, field
from MpDecorators import *
from MpBase import *
from typing import *


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
class MrMsCat(SimpleCatalogue):
    @classmethod
    def GetSeedData(cls):
        catseed = [MrMsCat().CatInit("DEU", "MR", "Herr"),
            	MrMsCat().CatInit("DEU", "MRS", "Frau"),
                MrMsCat().CatInit("GBR", "MR", "Mr."),
                MrMsCat().CatInit("GBR", "MRS", "Mrs.")]
        return catseed

@dataclass(init=False)
class GenderCat(SimpleCatalogue):
    @classmethod
    def GetSeedData(cls):
        catseed = [GenderCat().CatInit("DEU", "MALE", "männlich"),
                GenderCat().CatInit("DEU", "FEMALE", "weiblich"),
                GenderCat().CatInit("GBR", "MALE", "male"),
                GenderCat().CatInit("GBR", "FEMALE", "female")]
        return catseed

@dataclass(init=False)
class TitleCat(SimpleCatalogue):
    @classmethod
    def GetSeedData(cls):
        catseed = [TitleCat().CatInit("DEU", "DR", "Dr."),
                TitleCat().CatInit("DEU", "PHD", "PhD"),
                TitleCat().CatInit("DEU", "PROF", "Prof."),
                TitleCat().CatInit("GBR", "DR", "Prof."),
                TitleCat().CatInit("GBR", "PHD", "PhD"),
                TitleCat().CatInit("GBR", "PROF", "Dr.")]
        return catseed


        

@dataclass(init=False)
class MpAddress(): # has no id because it is always embedded
    zip : str = None
    city : str = None
    streetaddress : str = None
    country : str = None
    co : str = None
    
@dataclass(init=False)
class MpPerson(MpBase):
    firstname : str = None
    lastname : str = None
    gender : GenderCat = None
    mrms : MrMsCat = None
    title : TitleCat = None
    address : MpAddress = None
    email : str = None
    homephone : str = None
    mobilephone : str = None
    labels : List[str] = None

@dataclass(init=False)
class MpCompanyContact(MpPerson):
    jobtitle : str = None
    compphone : str = None
    companyid : str = None

@dataclass(init=False)
class MpCompany(MpBase):
    name : str = None
    bossid : str = None
    boss : MpCompanyContact = field(default=None,
                              metadata=MpSingleResolve.Map(localFieldName="bossid",
                                foreignFieldName="_id",
                                autofill=False,
                                othercls=MpCompanyContact))
    address : MpAddress = None
    contacts : List[MpCompanyContact] = field(default=None, 
                                        metadata=MpListResolve.Map(localFieldName="_id",
                                            foreignFieldName="companyid",
                                            autofill=False,
                                            othercls=MpCompanyContact))





