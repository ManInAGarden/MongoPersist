import mongopersist as mp

class TitleCat(mp.MpCatalog):
    _cattype = "TITLE"

class GenderCat(mp.MpCatalog):
    _cattype = "GENDER"

class MrMsCat(mp.MpCatalog):
    _cattype = "MRMS"

class MpAddress(mp.MpBase):
    Zip = mp.String()
    City = mp.String()
    StreetAddress = mp.String()
    Co = mp.String()

class MpPerson(mp.MpBase):
    Firstname = mp.String()
    Lastname = mp.String()
    Birthday = mp.DateTime()
    Gender = mp.Catalog(catalogtype=GenderCat)
    Mrms = mp.Catalog(catalogtype=MrMsCat)
    Title = mp.Catalog(catalogtype=TitleCat)
    Address = mp.EmbeddedObject(targettype=MpAddress)
    Email = mp.String()
    Homephone = mp.String()
    Mobilephone = mp.String()
    Labels = mp.EmbeddedList(targettype=str)

class MpEmployee(mp.MpBase):
    Jobtitle = mp.String()
    EmployeeNumber = mp.Int()
    Companyid = mp.String()
    Personid = mp.String()
    Person = mp.JoinedEmbeddedObject(targettype=MpPerson, localid=Personid, autofill=True)
    Isfixed = mp.Boolean()

class MpCompany(mp.MpBase):
    Name = mp.String()
    Address = mp.EmbeddedObject(targettype=MpAddress)
    Employees = mp.JoinedEmbeddedList(targettype=MpEmployee, foreignid=MpEmployee.Companyid, cascadedelete=True) #no autofill here for performance
