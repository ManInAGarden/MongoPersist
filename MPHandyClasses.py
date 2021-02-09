from types import LambdaType
import pymongo as pym
from bson.objectid import ObjectId
from dataclasses import dataclass, field
from typing import *
import mongopersist as mp

@dataclass(init=False)
class MrMsCat(mp.SimpleCatalogue):
    @classmethod
    def GetSeedData(cls):
        catseed = [MrMsCat().CatInit("DEU", "MR", "Herr"),
            	MrMsCat().CatInit("DEU", "MRS", "Frau"),
                MrMsCat().CatInit("GBR", "MR", "Mr."),
                MrMsCat().CatInit("GBR", "MRS", "Mrs.")]
        return catseed

@dataclass(init=False)
class GenderCat(mp.SimpleCatalogue):
    @classmethod
    def GetSeedData(cls):
        catseed = [GenderCat().CatInit("DEU", "MALE", "männlich"),
                GenderCat().CatInit("DEU", "FEMALE", "weiblich"),
                GenderCat().CatInit("GBR", "MALE", "male"),
                GenderCat().CatInit("GBR", "FEMALE", "female")]
        return catseed

@dataclass(init=False)
class TitleCat(mp.SimpleCatalogue):
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
class MpPerson(mp.MpBase):
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
class MpCompany(mp.MpBase):
    name : str = None
    bossid : str = None
    boss : MpCompanyContact = field(default=None,
                              metadata=mp.MpSingleResolve.Map(localFieldName="bossid",
                                foreignFieldName="_id",
                                autofill=False,
                                othercls=MpCompanyContact))
    address : MpAddress = None
    contacts : List[MpCompanyContact] = field(default=None, 
                                        metadata=mp.MpListResolve.Map(localFieldName="_id",
                                            foreignFieldName="companyid",
                                            autofill=False,
                                            othercls=MpCompanyContact))





