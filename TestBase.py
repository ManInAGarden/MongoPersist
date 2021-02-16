import unittest
import mongopersist as mp
from MpHandyClasses import *
import MockerParts as mocking
import json

class TestBase(unittest.TestCase):
    
    Mpf : mp.MpFactory = None #the persitence factory
    Mck : mocking.Mocker = None

    @classmethod
    def setUpClass(cls):
        cls.readini("utconfig.json")
        url = cls.getsetting("testurl")
        fact = mp.MpFactory(url, "MPTest")
        fact.lang = "DEU"
        mock = mocking.Mocker(fact)
        mock.create_seeddata("catseeds.json")
        cls.Mck = mock
        cls.Mpf = fact

    @classmethod
    def readini(cls, filepath):
        with open(filepath, 'r') as f:
            cls.settings = json.load(f)

    @classmethod
    def getsetting(cls, setgname):
        return cls.settings[setgname]
