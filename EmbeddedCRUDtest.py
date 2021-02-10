from DataMocker import DataMocker
import unittest
import mongopersist as mp
from MPHandyClasses import *
from TestBase import *

class EmbeddedCRUDtest(TestBase):
    def setUp(self):
        self.mocker = DataMocker(self.Mpf)
        self.Mpf.db.drop_collection(MpCompany.CollectionName())
        self.Mpf.db.drop_collection(MpCompanyContact.CollectionName())
        self.Mpf.db.drop_collection(MpBigCompany.CollectionName())
        super().setUp()

    def test_list_resolve(self):
        comp1 = self.mocker.createsmallcompany()
        comp = self.Mpf.findbyid(MpCompany, comp1._id)

        self.assertEqual(comp1._id, comp._id)

        self.Mpf.resolve(comp, "contacts")
        self.assertEqual(3, len(comp.contacts))

    def test_single_resolve(self):
        comp = self.mocker.createsmallcompany()
        boss = self.mocker.createcompanycontact(comp, firstname="Volker", lastname="Vorstand", jobtitle="Vorstandsvorsitzender")
        self.Mpf.flush(boss)
        comp.bossid = boss._id
        self.Mpf.flush(comp)

        compr = self.Mpf.findbyid(MpCompany, comp._id)
        self.Mpf.resolve(compr, "boss") #resolve by bossid as foreignkey into companycontacts

        self.assertIsNotNone(compr.boss)
        self.assertEqual(compr.boss.firstname, boss.firstname)
        self.assertEqual(compr.boss.lastname, boss.lastname)
        self.assertEqual("Vorstandsvorsitzender", compr.boss.jobtitle)


    def test_multiple_resolve(self):
        comp = self.mocker.createsmallcompany()
        boss = self.mocker.createcompanycontact(comp, firstname="Volker", lastname="Vorstand", jobtitle="Vorstandsvorsitzender")
        self.Mpf.flush(boss)
        comp.bossid = boss._id
        self.Mpf.flush(comp)

        compr = self.Mpf.findbyid(MpCompany, comp._id)
        self.Mpf.resolve(compr, "boss","contacts") #resolve the boss contact and also the contact/empolyees list of the company

        self.assertIsNotNone(compr.boss)
        self.assertIsNotNone(compr.contacts)
        self.assertTrue(type(compr.boss) is MpCompanyContact)
        self.assertTrue(type(compr.contacts) is list)
        self.assertEqual(4, len(compr.contacts))

    def test_multiple_resolve_andrewrite(self):
        comp = self.mocker.createsmallcompany()
        boss = self.mocker.createcompanycontact(comp, firstname="Volker", lastname="Vorstand", jobtitle="Vorstandsvorsitzender")
        self.Mpf.flush(boss)
        comp.bossid = boss._id
        self.Mpf.flush(comp)

        compr = self.Mpf.findbyid(MpCompany, comp._id)
        self.Mpf.resolve(compr, "boss","contacts") #resolve the boss contact and also the contact/empolyees list of the company

        self.assertIsNotNone(compr.boss)
        self.assertIsNotNone(compr.contacts)
        self.assertTrue(type(compr.boss) is MpCompanyContact)
        self.assertTrue(type(compr.contacts) is list)
        self.assertEqual(4, len(compr.contacts))

        #now that we have resolved we flush again an then make sure the resolved data are not written to the db
        #aka have to rsolved again
        self.Mpf.flush(compr)

        comprr = self.Mpf.findbyid(MpCompany, compr._id)
        self.assertIsNone(comprr.boss)
        self.assertIsNone(comprr.contacts)

    def test_bigcompany(self):
        bc = MpBigCompany()
        bc.name = "Big Company Selling Shit We Do Not Need SE"
        bc.isactive = True
        bc.foundationdate = datetime(1880, 7, 15)
        self.Mpf.flush(bc)

        bcr = self.Mpf.findbyid(MpBigCompany, bc._id)
        self.assertIsNotNone(bcr)
        self.assertEqual(bc.name, bcr.name)


if __name__ == '__main__':
    unittest.main()

