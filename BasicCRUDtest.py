import unittest
from DataMocker import DataMocker
from TestBase import TestBase
import MPFactory as mpf
from MPHandyClasses import *


class BasicMPCRUDTests(TestBase):

    def setUp(self) -> None:
        """set up before each test function call
        """
        self.mocker = DataMocker(self.Mpf)
        self.Mpf.db.drop_collection("MpPerson")
        super().setUp()

    def test_insert(self):
        p1 = self.mocker.createperson(firstname="Ingo", 
            lastname="Zanperoni", 
            gender=self.Mpf.cat(GenderCat,"MALE"),
            mrms=self.Mpf.cat(MrMsCat,"MR"),
            title=self.Mpf.cat(TitleCat, "PHD"))
            
        p1.homephone = "+49 201 55512348"
        p1.labels = ["Gartenbau", "RC-Modellflug"]
        
        p1.address = self.mocker.createaddress(zip="45130", city="Essen", streetaddress="Opernplatz 1")
        self.Mpf.flush(p1)

        p2 = self.Mpf.findbyid(MpPerson, p1._id)

        self.assertIsNotNone(p2)
        self.assertEqual(p1.firstname, p2.firstname)
        self.assertTrue(type(p2) is MpPerson)
        self.assertTrue(type(p2.address) is MpAddress)
        self.assertIn("Gartenbau", p2.labels)
        self.assertNotIn("Bier trinken", p2.labels)


    def test_findmany(self):
        p3 = self.mocker.createperson(firstname = "Gundula",
            lastname = "Gause",
            gender = self.Mpf.cat(GenderCat, "FEMALE"))

        self.Mpf.flush(p3)

        p4 = self.mocker.createperson(firstname = "Klaus",
            lastname = "Kleber",
            gender = self.Mpf.cat(GenderCat, "MALE"))

        
        p4.address = self.mocker.createaddress(zip = "45329",
            city = "Essen")

        p4.labels = ["3D-Druck","klassische Literatur","Horrorfilme"]
        self.Mpf.flush(p4)

        erg = self.Mpf.find(MpPerson, {})
        self.assertGreaterEqual(len(erg), 2)
        for p in erg:
            self.assertTrue(p.address == None or type(p.address) is MpAddress)

    
    def test_basicupdates(self):
        p1 = self.mocker.createperson(firstname = "Linda",
            lastname = "Zervakis",
            mrms = self.Mpf.cat(MrMsCat, "MRS"),
            gender =  self.Mpf.cat(GenderCat, "MALE")) #Uuups mistake, have to correct later

        self.Mpf.flush(p1)

        p1r = self.Mpf.findbyid(MpPerson, p1._id)
        self.assertEqual(p1.firstname, p1r.firstname)
        self.assertEqual(p1.lastname, p1r.lastname)
        self.assertEqual(p1.mrms.code, p1r.mrms.code)
        self.assertEqual(p1.mrms.value, p1r.mrms.value)
        self.assertEqual(p1.gender.code, "MALE")

        p1.gender = self.Mpf.cat(GenderCat, "FEMALE") # now it's correct
        p1.labels = ["Katzen", "Aquarium", "Telefonieren"]

        self.Mpf.flush(p1)
        p1r = self.Mpf.findbyid(MpPerson, p1._id)
        self.assertEqual(p1.firstname, p1r.firstname)
        self.assertEqual(p1.lastname, p1r.lastname)
        self.assertEqual(p1.mrms.code, p1r.mrms.code)
        self.assertEqual(p1.mrms.value, p1r.mrms.value)
        self.assertEqual(p1.gender.code, "FEMALE")
        self.assertTrue("Aquarium" in p1.labels)


if __name__ == '__main__':
    unittest.main()