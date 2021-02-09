import unittest
import mongopersist as mp
from MPHandyClasses import *
import json

class TestBase(unittest.TestCase):
    
    Mpf : mp.MpFactory = None #the persitence factory

    @classmethod
    def setUpClass(cls):
        cls.readini("utconfig.json")
        url = cls.getsetting("testurl")
        fact = mp.MpFactory(url, "MPTest")
        fact.lang = "DEU"
        fact.initseeddata(MrMsCat)
        fact.initseeddata(GenderCat)
        fact.initseeddata(TitleCat)
        cls.Mpf = fact

    @classmethod
    def readini(cls, filepath):
        with open(filepath, 'r') as f:
            cls.settings = json.load(f)

    @classmethod
    def getsetting(cls, setgname):
        return cls.settings[setgname]
