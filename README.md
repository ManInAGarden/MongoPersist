# MongoPersist

Framework to persist data from python classes to am mongodb documemt database

## Tiny tutorial

Just import MpFactory, instatiate an MpFactory like this:

    import mongopersist as mp

    fact = mp.MpFactory(url, "mptest")

Here mptest is the name of a mongodb database and url is a string filled with the URL for the db connection to a 
mongodb instance.

Now its all about having designed the data in python classes with the dataclass decorator. Maybe you want to store data for people like this:

    class MpPerson(mp.MpBase):
        Id = mp.String()
        Firstname = mp.String()
        Lastname = mp.String()
        Adr_street = mp.String()
        Adr_zip = mp.String()
        Adr_city= mp.String()

Note that we are using capitals for the class members defined here.

With that definition we can create a person now.

    pers = MpMyPerson()
    pers.firstname = "John"
    pers.lastname = "Nobody"
    pers.adr_street = "123 Times Square"
    pers.adr_city = "New York"
    ....
Note that we are using small letters as the first letters for the member names in the person instance here!

Now we store that person in our mongodb

    fact.flush(pers)

Note that we did not fill _id with any data!
Taking a look at the mongodb by using the tools after that fact.flush() we'll see that we have a new collection named MpPerson with the a single document in it. It looks like this:

    {
        "firstname " : "John",
        "lastname" : "Nobody"
        "street" : ".....
        "created" : <the time we created flushed the person in UTC>,
        "lastupdate" : <same as created for now>
    }

Now we can use the factory to find that person later on

    plater = fact.find(MpMyPerson, MpMyPerson.Firstname="John")

Off course that only does work because there's only one person called John in the collection now. Maybe you notices the fields "_id", "created" and "lastupdate". They are defined in mp.MpBase class from which MpMyPerson is derived.

The person's data can be now retrieved like this:
    
    print(plater.firstname + " " + plater.lastname)

You'll find am more sophistiacated version of a person class in MpHandyClasses along with everything you need for simple catalogs line in titles (PhD. Prof. etc).

## More complicated data

Life most of the time is'nt as easy as in the tiny tutorial above. Real data are much more complicated. Instead of having just plain classes with data storage in one collecion per class and one document for each instance we have things like embedded members, lists of embedded members, joined embedded members and also list of joined embedded members. Lets see what this is and how this can be done with mongopersist.

Lets try to store company data in a mongodb. We could have hour company data like this:

class MpAddress(mp.MpBase):
    """class used for defining and storing addresses
    """
    Zip = mp.String()
    City = mp.String()
    StreetAddress = mp.String()
    Co = mp.String()

    class MpPerson(mp.MpBase):
        Id = mp.String()
        Firstname = mp.String()
        Lastname = mp.String()
        Address = EmbeddedObject(targettype=MpAddress)
        

    class MpCompany(mp.MpBase):
        """class for defining and storing companies
        """
        Name = String()
        Phone = String()
        Address = EmbeddedObject(targettype=MpAddress)
        Employees = mp.EmbeddedList(targettype=MpPerson)

So what does this do? When we create and store a companies data like this:

    import mongopersist as mp

    fact = mp.MpFactory(url, "mptest")

    comp = MpCompany(name="testco", phone="+31.1241555-5555",
        address=MpAddress(zip="12345", city="Phantasy Town", streetaddress="123a Road To Nowhere"))

    com.employees = []
    for i in range(20):
        emp = MpPerson(firstname=str(i), lastname="Nobody")
        comp.employees.append(emp)

    fact.flush(comp)

Looking into the database we'd see that the company was stored in a collection called *MpCompany* in single document. This document has 20 sub-documents arranged in a list in a field called "employees", one for each person we added. The companies address also is a subdocument stored inside the person-document.

When the company gets deleted all the persons will also be deleted along with all the companies data. Maybe that's what we want to have and for many uses cases this is quite sufficient. But what if we want to store data for many companies and if we have people working for more than one of theses companies? Then we need to separate the companies and the people each into its own collection.

We leave MpPeople and MpAddress as it is but change the company and add a new class for storing employee data.

    class MpEmployee(mp.MpBase):
        Jobtitle = mp.String()
        EmployeeNumber = mp.Int()
        Companyid = mp.String()
        Personid = mp.String()
        Person = mp.JoinedEmbeddedObject(targettype=MpPerson, localid=Personid, autofill=True)

    class MpCompany(mp.MpBase):
        Name = mp.String()
        Address = mp.EmbeddedObject(targettype=MpAddress)
        Employees = mp.JoinedEmbeddedList(targettype=MpEmployee, foreignid=MpEmployee.Companyid, cascadedelete=True)

Here we have employees with a data field called *Companyid* which will store the id of the company which employs the employee. It is a foreign key to the company. Additionaly the employee also has a foreign key called *Personid* pointing to the person's data.

May be you already have noticed that every document automatically gets some kind of cryptic id stored in field called *_id*. By storing the ids of other documents one can store a reference to another document. That's what we call a foreign key here. By declaring employees in separate documents and storing the foreign key to the person and to a company in them we can have a person work for as many companies as we want.

But what do we have to do to store a companies data now?

    import mongopersist as mp

    fact = mp.MpFactory(url, "mptest")

    comp1 = MpCompany(name="testco", phone="+31.1241555-5555",
        address=MpAddress(zip="12345", city="Phantasy Town", streetaddress="123a Road To Nowhere"))
    fact.flush(comp1)
    
    comp2 = MpCompany(name="testco2", phone="+31.1241555-5556",
        address=MpAddress(zip="12345", city="Phantasy Town", streetaddress="123b Road To Nowhere"))
    
    fact.flush(comp2)
    people = []
    for i in range(40):
        people[i] = MpPerson(firstname=str(i), lastname="Nobody")
        fact.flush(pers)

    #now we have to companies and 40 yet unemployed people

    #let's get the first 25 a job in comp1 and the last 25 a job in comp2

    for i in range(25):
        emp = MpEmployee(employeenumber=i, companyid = comp1._id, personid=people[i]._id)
        fact.flush(emp)

    for i in range(25):
        pidx = len(people) - i - 1
        emp = MpEmployee(employeenumber=i, companyid = comp2._id, personid=people[pidx]._id)
        fact.flush(emp)

Now let's read the data from the database:

    testco = fact.find_one(MpCompany, {"name:"testco"})

Looking at the data in testco with the python debugger stopped right behind that statement will show that all the foreign keys are filled but the employee list is still None. This is becaus we defined *autofill=False* in the field's definition. This is for performance reasons. Not always when a company is retireved from the database all the employees are needed. This is done by resolving the embedded data we need like this:

    fact.resolve(testco, MpCompany.Employees)

After that we find all the employees in testco.employees.

## Finding data the easy way

Finding data by writing down the search criteria in form of a dictionary can produce a lot of errors because nothing helps us to use the correct spelling for the field names. That's why we can also *find* data in a more sophisticated way.

Try this:

    comp = MpQuery(fact, MpCompany).where(MpCompany.Name.regex("^testco").orderby(MpCompanyName).first()

Read it from left to right. Here we define a query operating the factory and the class *MpCompany*. The where produces an iterable object which is prepared to issue a find-operartion on the database. This is not done right now because the *orderby* after that adds ordering to the database find. At last we have a first which tries to get the first element of that iterable. Only now the find is executed so that first can return the first company retrieved from the database with a name matching the given regex (name should start with the letter *t*).

Or try this:

    q = MpQuery(fact, MpEmpoyee).where(employeenumber >5)

    for emp in q:
        print(emp.employeenumber, emp.person.firstname, emp.person.lastname)

Here we do not use first to get the first the employee. So we can iterate over the query *q* to get all the employees one by one and print some of their attributes. Note that we can directly uses the person data because here we have *autofill=True* for the field *Person*.
