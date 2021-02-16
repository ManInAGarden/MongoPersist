import mongopersist as mp
from MpHandyClasses import *
import unittest
from TestBase import *

class CrudTest(TestBase):

    def setUp(self):
        super().setUp()

    def test_get_mogo_dict(self):
        p = MpPerson(firstname="Paul", lastname="McCartney", address=MpAddress(zip="BL12412", city="Bristol"))

        md = self.Mpf._get_mongodict(p)

        self.assertIsNotNone(md)
        self.assertIsInstance(md, dict)
        self.assertEqual(md["firstname"], "Paul")
        self.assertEqual(md["address"]["city"], "Bristol")

    def test_create_instance(self):
        p = MpPerson(firstname="Paul", lastname="McCartney", address=MpAddress(zip="BL12412", city="Bristol"))

        md = {"firstname": "John", "lastname":"Lennon", "address":{"zip":"BL141312", "city":"Bristol"}}

        self.assertIsNotNone(md)
        p = self.Mpf._create_inst(MpPerson, md)
        self.assertIsNotNone(p)
        self.assertEqual(p.firstname, "John")
        self.assertEqual(p.address.city, "Bristol")


    
if __name__ == '__main__':
    unittest.main()