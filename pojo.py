import peewee as pw

myDB = pw.MySQLDatabase('drcrawler', host='localhos', port=3306, user='root', passwd='root')


class MySQLModel(pw.Model):
    """A base model that will use our MySQL database"""
    class Meta:
        database = myDB

class User(MySQLModel):
    username = pw.CharField()
    # etc, etc


# when you're ready to start querying, remember to connect
myDB.connect()
