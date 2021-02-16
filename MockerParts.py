import importlib
import json
from mongopersist.BasicClasses import MpBase, MpCatalog
import mongopersist as mp
from MpHandyClasses import *

class Mocker(object):
   
    def __init__(self, fact : mp.MpFactory) -> None:
        self._mpf = fact

    def create_person(self, **kwargs):
        p = MpPerson(**kwargs)
        self._mpf.flush(p)
        return p

    def create_seeddata(self, filepath):
        self._mpf._db.drop_collection(MrMsCat.get_collection_name()) #this drops all of the catalogs becaus they are all in the same collection!
        seeder = Seeder(self._mpf, filepath)
        seeder.create_seeddata()

    def create_company(self, name, numemps):
        comp = MpCompany(name="Unit Test CORP")
        self._mpf.flush(comp)
        for i in range(numemps):
            p = MpPerson(firstname="Willy", lastname="Winzig")
            self._mpf.flush(p)
            emp = MpEmployee(employeenumber=i+1, companyid=comp._id, personid=p._id, jobtitle="Subalterner")
            self._mpf.flush(emp)

        return comp

class Seeder(object):
    def __init__(self, fact, filepath) -> None:
        self._filepath = filepath
        self._fact = fact
        super().__init__()

    def create_seeddata(self):
        with open(self._filepath, 'r', encoding="utf8") as f:
            data = json.load(f)
        
        for datk, datlist in data.items():
            cls = self._getclass(datk)
            colname = cls.get_collection_name()
            for datmap in datlist:
                s = cls(**datmap)
                self._fact.flush(s)

    def _getclass(self, clsname : str):
        if clsname is None or len(clsname)==0:
            raise Exception("Mocker._getclass(classname) for an empty classname is not a valid call")

        lastdot = clsname.rindex('.')
        modulename = clsname[0:lastdot]
        clsname = clsname[lastdot + 1::]
        module = importlib.import_module(modulename)
        return getattr(module, clsname)

