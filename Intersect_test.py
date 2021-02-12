import unittest

from MPHandyClasses import MpBigCompany, MpBigCompany2Contact, MpPerson
from DataMocker import DataMocker
from TestBase import TestBase


class IntersectTest(TestBase):
    def setUp(self) -> None:
        """set up before each test function call
        """
        self.mocker = DataMocker(self.Mpf)
        self.Mpf.db.drop_collection(MpBigCompany.CollectionName())
        self.Mpf.db.drop_collection(MpPerson.CollectionName())
        self.Mpf.db.drop_collection(MpBigCompany2Contact.CollectionName())
        super().setUp()

    def test_empolyee_intersect(self):
        bigc = self.mocker.createbigcompany("BigtradeUT SE")
        empfirst = ["John", "Jane", "French"]
        emplast = ["Doe", "Doe", "Fries"]
        emppos = ["slave", "worker", "boss"]
        for i in range(len(empfirst)):
            self.mocker.addbigemployee(bigc, firstname=empfirst[i], lastname = emplast[i], position=emppos[i])

        bigcr = self.Mpf.findbyid(MpBigCompany, bigc._id)
        self.Mpf.resolve(bigcr, "employees")
        self.assertIsNotNone(bigcr.employees)
        self.assertEqual(len(empfirst), len(bigcr.employees))

        for emp in bigcr.employees:
            self.assertIn(emp.firstname, empfirst)
            self.assertIn(emp.lastname, emplast)


if __name__ == '__main__':
    unittest.main()

