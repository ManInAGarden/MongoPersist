from MPHandyClasses import MpCompany, MpCompanyContact, MpPerson
from TestBase import TestBase
import unittest
from MpBase import *
import dataclasses as dc

class BaseClassTest(TestBase):
    def setUp(self):
        pass

    def test_NonableDateTime(self):
        dtn = NoneableDateTime(None)

        self.assertFalse(dtn.hasvalue())
        self.assertIsNone(dtn.value)

        tstt = dt.datetime.now()
        dtn = NoneableDateTime(tstt)
        self.assertTrue(dtn.hasvalue())
        self.assertEqual(tstt, dtn.value)

        dtn = NoneableDateTime(True)

    def test_NullableBool(self):
        bn = NoneableBool(None)
        self.assertFalse(bn.hasvalue())
        self.assertIsNone(bn.value)
        
        bn = NoneableBool(True)
        self.assertTrue(bn.hasvalue())
        self.assertTrue(bn.value)

    def test_createinstance(self):
        dcodict = {"firstname" : "Total",
            "lastname":"Künstlich"}

        insta = self.Mpf.createinstance(MpPerson, dcodict)
        self.assertEqual(insta.firstname, "Total")
        self.assertEqual(insta.lastname, "Künstlich")
        self.assertIsNone(insta.gender)
        self.assertIsNone(insta.created)

    def test_issingleresolveable(self):
        self.assertFalse(self.Mpf.issingleresolveable(self.findfield(MpCompany, "contacts")))
        self.assertTrue(self.Mpf.issingleresolveable(self.findfield(MpCompany, "boss")))
        self.assertFalse(self.Mpf.issingleresolveable(self.findfield(MpPerson, "gender")))
        self.assertFalse(self.Mpf.issingleresolveable(self.findfield(MpPerson, "lastname")))


    def findfield(self, cls, name):
        fields = dc.fields(cls)

        answ = None
        for field in fields:
            if field.name == name:
                answ = field
                break

        if answ is None:
            raise Exception("Field {} not found in class {}".format(name, cls))

        return answ

if __name__ == '__main__':
    unittest.main()
