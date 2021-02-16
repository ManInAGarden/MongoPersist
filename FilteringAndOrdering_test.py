from mongopersist.FactoryParts import MpQuery
from MpHandyClasses import *
import MockerParts as mocking
from TestBase import TestBase
import datetime as dt
import unittest

class CrudTest(TestBase):

    def setUp(self):
        self.Mpf._db.drop_collection("MpPerson")
        self.Mpf._db.drop_collection("MpCompany")
        self.Mpf._db.drop_collection("MpEmployee")
        super().setUp()
    
    def test_simple_where(self):
        p1 = self.Mck.create_person(
                     firstname="Mensch", lastname="Meier",
                     gender = self.Mpf.cat(GenderCat, "MALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MR"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"),
                     labels=["3D-printing", "pillow fights"])

        self.Mpf.flush(p1)
        fname = "Mensch"
        quer = MpQuery(self.Mpf, MpPerson).where((MpPerson.Firstname==mp.v(fname)) & (MpPerson.Lastname==mp.v("Meier")))

        for pers in quer:
            self.assertEqual(pers.firstname, "Mensch")

    def test_not_so_simple_where(self):
        p1 = self.Mck.create_person(
                     firstname="Mensch", lastname="Meier",
                     birthday=dt.datetime(1988,6,25),
                     gender = self.Mpf.cat(GenderCat, "MALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MR"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"),
                     labels=["3D-printing", "pillow fights"])

        p1 = self.Mck.create_person(
                     firstname="Halöchen", lastname="Popöchen",
                     birthday=dt.datetime(1960,3,30),
                     gender = self.Mpf.cat(GenderCat, "FEMALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MRS"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"),
                     labels=["3D-printing", "pillow fights"])

        self.Mpf.flush(p1)
        quer = MpQuery(self.Mpf, MpPerson).where(MpPerson.Birthday < mp.v(dt.datetime(1970,12,31)))

        for pers in quer:
            self.assertEqual(pers.firstname, "Halöchen")

if __name__ == '__main__':
    unittest.main()