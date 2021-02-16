from MpHandyClasses import *
import MockerParts as mocking
from TestBase import TestBase
import unittest

class CrudTest(TestBase):

    def setUp(self):
        self.Mpf._db.drop_collection("MpPerson")
        self.Mpf._db.drop_collection("MpCompany")
        self.Mpf._db.drop_collection("MpEmployee")
        super().setUp()

    def test_create_and_init(self):
        p1 = MpPerson(firstname="Mensch", lastname="Meier",
                        address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"))
        self.assertEqual(p1.firstname, "Mensch")
        self.assertEqual(p1.lastname, "Meier")
        self.assertIsNone(p1.birthday)
        self.assertIsNone(p1._id)
        self.assertIsNone(p1.created)
        self.assertIsNone(p1.lastupdate)
        self.assertIsNotNone(p1.address)
        self.assertIsInstance(p1.address, MpAddress)
        self.assertEqual(p1.address.zip, "45329")

    def test_cataloging(self):
        oldlang = self.Mpf._lang

        self.Mpf._lang = "GBR"
        mrms = self.Mpf.cat(MrMsCat, "MR")
        self.assertEqual(mrms.code, "MR")
        self.assertEqual(mrms.value, "Mr.")
        self.Mpf._lang = "DEU"
        mrmsdeu = self.Mpf.cat(MrMsCat, "MR")
        self.assertEqual(mrmsdeu.code, "MR")
        self.assertEqual(mrmsdeu.value, "Herr")

        self.Mpf._lang = oldlang


    def test_first_flush(self):
        p1 = self.Mck.create_person(
                     firstname="Mensch", lastname="Meier",
                     gender = self.Mpf.cat(GenderCat, "MALE"),
                     mrms = self.Mpf.cat(MrMsCat, "MR"),
                     address = MpAddress( zip="45329", city="Essen", streetaddress="Altenessener Str. 112"),
                     labels=["3D-printing", "pillow fights"])

        self.Mpf.flush(p1)

        p1r = self.Mpf.find(MpPerson, p1)
        self.assertEqual(p1r._id, p1._id)
        self.assertEqual(p1r.firstname, p1.firstname)
        self.assertCountEqual(p1r.labels, p1.labels)
        self.assertIsNotNone(p1r.address)
        self.assertIsInstance(p1r.address, MpAddress)
        self.assertEqual(p1r.mrms.code, "MR")
        self.assertEqual(p1r.gender.code, "MALE")

    def test_joins(self):
        comp = self.Mck.create_company("Murks & Co", 3)
        compr = self.Mpf.find(MpCompany, comp)
        self.assertIsNone(compr.employees)
        self.Mpf.resolve(compr, MpCompany.Employees)
        self.assertIsNotNone(compr.employees)
        self.assertEqual(len(compr.employees), 3)

    def test_delete_cascades(self):
        comp = self.Mck.create_company("Murks & Co", 3)
        self.Mpf.resolve(comp, MpCompany.Employees)

        compr = self.Mpf.find(MpCompany, comp)
        
        self.Mpf.delete(compr)

        for employee in comp.employees:
            self.assertIsNone(self.Mpf.find(MpEmployee, employee)) #this is deleted by cascade
            self.assertIsNotNone(self.Mpf.find(MpPerson, employee.person)) #but not down to the person



if __name__ == '__main__':
    unittest.main()