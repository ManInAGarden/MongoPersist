# MongoPersist

Framework to persist data from python classes to am mongodb documemt database

## Tiny tutorial

Just import MpFactory, instatiate an MpFactory like this

    fact = MpFactory(url, "mptest")

Here mptest is the name of a mongodb database and url is a stringng filled with the URL for the db connection to a 
mongodb.

Now its all abour having designed the data in python classes with the dataclass decorator. Maybe you want to store data for people like this:


    @dataclass(init=false)
    class MpPerson():
        _id : str = None
        firstname : str = None
        lastname : str = None
        adr_street : str = None
        adr_zip : str = None
        adr_city : str = None

With that definition we can create a person now.

    pers = MpMyPerson(MpBase)
    pers.firstname = "John"
    pers.lastname = "Nobody"
    pers.street = "123 Times Square"
    ....

and store that person in hour mongodb

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

    plater = fact.find_one(MpMyPerson, {"firstname":"John"})

Off course that only does work because there's only on person called John in the collection now. Mybe you notices the fields "_id", "created" and "lastupdate". They are defined in MpBase class from which MpMyPerson is derived. Youll find it in MpHandyClasses along with a more sophisticated version of a person class (MpPerson) and other nice classes.