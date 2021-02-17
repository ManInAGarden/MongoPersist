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

        quer = MpQuery(self.Mpf, MpPerson).where().order_by(MpPerson.Lastname.desc()) #descending ordering
        nalt = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        for p in quer:
            self.assertLessEqual(p.lastname, nalt)
            nalt = p.lastname

    def test_select(self):
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
        p3 = self.Mck.create_person(
                     firstname="Linda", lastname="Zervakis",
                     birthday=dt.datetime(1975,5,17),
                     gender = self.Mpf.cat(GenderCat, "FEMALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MRS"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"),
                     labels=["3D-printing", "italian wine"])
        p4 = self.Mck.create_person(
                     firstname="Karen", lastname="Miosga",
                     birthday=dt.datetime(1970,2,28),
                     gender = self.Mpf.cat(GenderCat, "FEMALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MRS"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"),
                     labels=["3D-printing", "french wine"])

        quer = MpQuery(self.Mpf, MpPerson).where(MpPerson.Gender=="FEMALE").select(lambda p:(p.lastname, p.firstname))
        accept = [("Gause", "Gundula"), ("Miosga","Karen"), ("Zervakis","Linda")]
        for item in quer:
            self.assertTrue(item in accept)

    def test_subitem_where(self):
        p1 = self.Mck.create_person(
                     firstname="Klaus", lastname="Kleber",
                     birthday=dt.datetime(1988,6,25),
                     gender = self.Mpf.cat(GenderCat, "MALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MR"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Gartenweg 18"),
                     labels=["3D-printing", "italian wine"])
        p2 = self.Mck.create_person(
                     firstname="Gundula", lastname="Gause",
                     birthday=dt.datetime(1960,3,30),
                     gender = self.Mpf.cat(GenderCat, "FEMALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MRS"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"),
                     labels=["3D-printing", "french wine"])
        p3 = self.Mck.create_person(
                     firstname="Linda", lastname="Zervakis",
                     birthday=dt.datetime(1975,5,17),
                     gender = self.Mpf.cat(GenderCat, "FEMALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MRS"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 113"),
                     labels=["3D-printing", "italian wine"])
        p4 = self.Mck.create_person(
                     firstname="Karen", lastname="Miosga",
                     birthday=dt.datetime(1970,2,28),
                     gender = self.Mpf.cat(GenderCat, "FEMALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MRS"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Vogelheimer Str. 12"),
                     labels=["3D-printing", "french wine"])

        for p in MpQuery(self.Mpf, MpPerson).where(MpPerson.Address.sub(MpAddress.StreetAddress)=="Altenessener Str. 112"):
            self.assertEqual(p.address.streetaddress, "Altenessener Str. 112")

    def test_isin(self):
        p1 = self.Mck.create_person(
                     firstname="Klaus", lastname="Kleber",
                     birthday=dt.datetime(1988,6,25),
                     gender = self.Mpf.cat(GenderCat, "MALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MR"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Gartenweg 18"),
                     labels=["3D-printing", "italian wine"])
        p2 = self.Mck.create_person(
                     firstname="Gundula", lastname="Gause",
                     birthday=dt.datetime(1960,3,30),
                     gender = self.Mpf.cat(GenderCat, "FEMALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MRS"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"),
                     labels=["3D-printing", "french wine"])
        p3 = self.Mck.create_person(
                     firstname="Linda", lastname="Zervakis",
                     birthday=dt.datetime(1975,5,17),
                     gender = self.Mpf.cat(GenderCat, "FEMALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MRS"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 113"),
                     labels=["3D-printing", "italian wine"])
        p4 = self.Mck.create_person(
                     firstname="Karen", lastname="Miosga",
                     birthday=dt.datetime(1970,2,28),
                     gender = self.Mpf.cat(GenderCat, "FEMALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MRS"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Vogelheimer Str. 12"),
                     labels=["3D-printing", "french wine"])

        quer = MpQuery(self.Mpf,MpPerson).where(MpPerson.Gender.isin(["MALE","FEMALE"]))
        malect = 0
        femalect = 0
        for p in quer:
            if p.gender.code == "MALE": malect+=1
            elif p.gender.code=="FEMALE": femalect+=1

        self.assertGreater(malect, 0)
        self.assertGreater(femalect, 0)

        quer = MpQuery(self.Mpf,MpPerson).where(MpPerson.Firstname.isin(["Linda","Karen"]) & MpPerson.Gender.isin(["MALE","FEMALE"]))
        for p in quer:
            self.assertTrue(p.firstname in ["Karen", "Linda"])

    def test_regex(self):
        p1 = self.Mck.create_person(
                     firstname="Klaus", lastname="Kleber",
                     birthday=dt.datetime(1988,6,25),
                     gender = self.Mpf.cat(GenderCat, "MALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MR"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Gartenweg 18"),
                     labels=["3D-printing", "italian wine"])
        p2 = self.Mck.create_person(
                     firstname="Gundula", lastname="Gause",
                     birthday=dt.datetime(1960,3,30),
                     gender = self.Mpf.cat(GenderCat, "FEMALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MRS"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"),
                     labels=["3D-printing", "french wine"])
        p3 = self.Mck.create_person(
                     firstname="Linda", lastname="Zervakis",
                     birthday=dt.datetime(1975,5,17),
                     gender = self.Mpf.cat(GenderCat, "FEMALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MRS"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 113"),
                     labels=["3D-printing", "italian wine"])
        p4 = self.Mck.create_person(
                     firstname="Karen", lastname="Miosga",
                     birthday=dt.datetime(1970,2,28),
                     gender = self.Mpf.cat(GenderCat, "FEMALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MRS"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Vogelheimer Str. 12"),
                     labels=["3D-printing", "french wine"])

        quer = MpQuery(self.Mpf,MpPerson).where(MpPerson.Firstname.regex("^L"))

        for p in quer:
            self.assertEqual(p.firstname[0], "L")

        quer = MpQuery(self.Mpf,MpPerson).where(MpPerson.Firstname.regex("^a"))

        for p in quer:
            lidx = len(p.firstname) - 1
            self.assertEqual(p.firstname[lidx], "a")

        quer = MpQuery(self.Mpf,MpPerson).where(MpPerson.Address.sub(MpAddress.StreetAddress).regex(".Str."))
        ct = 0
        for p in quer:
            self.assertIn("Str", p.address.streetaddress)
            ct += 1
            
        self.assertEqual(ct, 3)


if __name__ == '__main__':
    unittest.main()