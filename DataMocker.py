import mongopersist as mp
from MPHandyClasses import *

class DataMocker():
    def __init__(self, mpf):
        self._mpf = mpf

    def createperson(self, 
        firstname : str ="Tester", 
        lastname : str="Testmann", 
        gender : GenderCat = None, 
        mrms : MrMsCat=None, 
        title : TitleCat=None) -> MpPerson:

        answ = MpPerson()
        answ.firstname = firstname
        answ.lastname = lastname
        answ.gender = gender
        answ.mrms = mrms
        answ.title = title

        self._mpf.flush(answ)

        return answ

    def createaddress(self,
        zip = "45329",
        city = "Essen",
        country = "DEU",
        streetaddress = "Altenessener Str. 112") -> MpAddress:

        answ = MpAddress()
        answ.country = country
        answ.zip = zip
        answ.city = city
        answ.streetaddress = streetaddress

        return answ

    def addaddress(self, p : MpPerson, adr : MpAddress):
        p.address = adr

    def createcompany(self, name="Lach und Schießgesellschaft", address = None):
        comp = MpCompany()
        comp.name = name
        if address is None:
            addr = self.createaddress(country="DEU", zip="8000", city="München", streetaddress="Stachus 7")
        else:
            addr = address

        comp.address = addr
        self._mpf.flush(comp)
        
        return comp

    def createcompanycontact(self, comp : MpCompany, mrms : MrMsCat=None, firstname:str = "Servus", lastname : str="Sklave", jobtitle: str="Subalterner") -> MpCompanyContact:
        if comp is None:
            raise Exception("None Compony is not supported in createcompanycontact of DataMocker")

        cc = MpCompanyContact()
        cc.firstname = firstname
        cc.lastname = lastname
        cc.jobtitle = jobtitle
        cc.mrms = mrms
        cc.companyid = comp._id

        return cc

    def createsmallcompany(self):
        comp = self.createcompany()
        self._mpf.flush(comp)

        cc1 = self.createcompanycontact(comp, 
            firstname = "Servus",
            lastname = "Sklave",
            jobtitle = "Subalterner",
            mrms = self._mpf.cat(MrMsCat,"MR"))

        self._mpf.flush(cc1)

        cc2 = self.createcompanycontact(comp,
            firstname = "Boss",
            lastname = "Chef",
            jobtitle = "Vorgesetzter",
            mrms = self._mpf.cat(MrMsCat,"MR"))

        self._mpf.flush(cc2)

        cc3 = self.createcompanycontact(comp,
            firstname = "Serva",
            lastname = "Sklavin",
            jobtitle = "Subalterner",
            mrms = self._mpf.cat(MrMsCat,"MRS"))

        self._mpf.flush(cc3)
        
        return comp

    def createbigcompany(self, name : str ="Noname SE", establishedsince : datetime = None) -> MpBigCompany:
        bc = MpBigCompany()
        bc.name = name
        bc.establishedsince = establishedsince
        bc.isactive = True
        self._mpf.flush(bc)
        
        return bc

    def addbigemployee(self, bigc, firstname="Billy", lastname="Looser", position="worker", empstart=None) -> MpPerson:
        p = MpPerson()
        p.firstname = firstname
        p.lastname = lastname
        self._mpf.flush(p)

        cip = MpBigCompany2Contact()
        cip.position = position
        cip.parentid = bigc._id
        cip.targetid = p._id
        cip.employmentstart = empstart
        self._mpf.flush(cip)

        return p
