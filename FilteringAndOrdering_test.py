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
        quer = MpQuery(self.Mpf, MpPerson).where((MpPerson.Firstname==fname) & (MpPerson.Lastname=="Meier"))

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

        p2 = self.Mck.create_person(
                     firstname="Halöchen", lastname="Popöchen",
                     birthday=dt.datetime(1960,3,30),
                     gender = self.Mpf.cat(GenderCat, "FEMALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MRS"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"),
                     labels=["3D-printing", "pillow fights"])

        self.Mpf.flush(p1)
        quer = MpQuery(self.Mpf, MpPerson).where(MpPerson.Birthday < dt.datetime(1970,12,31))

        for pers in quer:
            self.assertEqual(pers.firstname, "Halöchen")

    def test_first_or_default(self):
        p1 = self.Mck.create_person(
                     firstname="Klaus", lastname="Kleber",
                     birthday=dt.datetime(1988,6,25),
                     gender = self.Mpf.cat(GenderCat, "MALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MR"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"),
                     labels=["3D-printing", "italian wine"])

        p2 = self.Mck.create_person(
                     firstname="Gundula", lastname="Gause",
                     birthday=dt.datetime(1960,3,30),
                     gender = self.Mpf.cat(GenderCat, "FEMALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MRS"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"),
                     labels=["3D-printing", "french wine"])

        first = MpQuery(self.Mpf, MpPerson).first_or_default(None) #no where so we expect all results
        self.assertIsNotNone(first)
        self.assertTrue(first._id==p1._id or first._id == p2._id)

        first = MpQuery(self.Mpf, MpPerson).where((MpPerson.Firstname=="Friedrich") & (MpPerson.Lastname=="Kleber")).first_or_default(None) #query with no result
        self.assertIsNone(first)

    def test_first(self):
        with self.assertRaises(Exception):
            first = MpQuery(self.Mpf, MpPerson).where().first() #query with no result because we have not produced any data

        p1 = self.Mck.create_person(
                     firstname="Klaus", lastname="Kleber",
                     birthday=dt.datetime(1988,6,25),
                     gender = self.Mpf.cat(GenderCat, "MALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MR"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"),
                     labels=["3D-printing", "italian wine"])

        p2 = self.Mck.create_person(
                     firstname="Gundula", lastname="Gause",
                     birthday=dt.datetime(1960,3,30),
                     gender = self.Mpf.cat(GenderCat, "FEMALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MRS"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"),
                     labels=["3D-printing", "french wine"])

        first = MpQuery(self.Mpf, MpPerson).where().first() #now we should find at least one person
        self.assertIsNotNone(first)
        self.assertIsInstance(first, MpPerson)

    def test_order_by(self):
        p1 = self.Mck.create_person(
                     firstname="Klaus", lastname="Kleber",
                     birthday=dt.datetime(1988,6,25),
                     gender = self.Mpf.cat(GenderCat, "MALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MR"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"),
                     labels=["3D-printing", "italian wine"])

        p2 = self.Mck.create_person(
                     firstname="Gundula", lastname="Gause",
                     birthday=dt.datetime(1960,3,30),
                     gender = self.Mpf.cat(GenderCat, "FEMALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MRS"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"),
                     labels=["3D-printing", "french wine"])

        quer = MpQuery(self.Mpf, MpPerson).where().order_by(MpPerson.Birthday, MpPerson.Lastname)

        balt = dt.datetime(1900,1,1) #very very old
        for p in quer:
            self.assertGreaterEqual(p.birthday, balt)
            balt = p.birthday

        quer = MpQuery(self.Mpf, MpPerson).where().order_by(MpPerson.Lastname.desc())
        nalt = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        for p in quer:
            self.assertLessEqual(p.lastname, nalt)
            nalt = p.lastname

if __name__ == '__main__':
    unittest.main()