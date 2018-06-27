import sqlite3
import time
import datetime
import faker
import peewee

conn = sqlite3.connect(':memory:') # while creating it cause it run again and again.
conn = sqlite3.connect('participants.db') # Activate this one later and delete the one above...

c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS participants (
  first text,
  last text,
  ID integer,
  year_of_birth integer,
  dominant_hand text,
  mail text,
  notes text,
  experiments blob
  )""")


c.execute("INSERT INTO participants VALUES (:first,:last,:ID,:experiments,:year_of_birth,:dominant_hand,:mail,:notes)",
          {'first': 'YO', 'last': 'BO', 'ID':'123234345', 'experiments': "{'name':'HRS', 'Completed': 1, 'date': '12-12-2018'}",
           'year_of_birth':'','dominant_hand': '','mail':'','notes':''})


def insert_sub(sub):
    with conn:
        c.execute("INSERT INTO participants VALUES (:first,:last,:withfloat,:withint)",
                  {'first': sub.first, 'last': sub.last, 'withfloat': sub.withfloat, 'withint': sub.withint})

def remove_sub(sub):
    with conn:
        c.execute("DELETE from participants WHERE first = :first AND last = :last",
                  {'first': sub.first, 'last': sub.last})

def update_thing(sub,thing):
    with conn:
        c.execute("""UPDATE participants SET thing = :thing
                    WHERE first = :first AND last = :last""",
                  {'first': sub.first, 'last': sub.last})

def get_sub_by_name(lastname):
    c.execute("SELECT * FROM participants WHERE last=:last", {'last': lastname})
    return c.fetchall()


def read_from_db():
    c.execute('SELECT * FROM participants')
    data = c.fetchall()
    print(data)



print(c.fetchone())

#c.fetchmany()
c.fetchall() # puts it in a list

conn.commit()
c.close
conn.close()




----
unix = time.time()
timestamp = datetime.datetime.fromtimestamp(unix).strftime(('%d-%m-%Y %H:%M'))

c.execute("DROP TABLE participants")


# maybe use with for automatic coomit etc.




-----
c.execute("INSERT INTO participants VALUES ('YOHO','BO','72.4','8')")

c.execute("INSERT INTO participants VALUES (?,?,?,?)", (sub1.first,))

c.execute("INSERT INTO participants VALUES (:first,:last,:withfloat,:withint)",
          {'first': sub1.first, 'last': sub1.last, 'withfloat': sub1.withfloat, 'withint': sub1.withint})

c.execute("SELECT first, last FROM participants WHERE last=:last", {'last': 'BO'})



c.execute("SELECT * FROM participants WHERE last='BO'")
------


from peewee import *

db = SqliteDatabase('people.db')

class Person(Model):
    name = CharField()
    birthday = DateField()

    class Meta:
        database = db # This model uses the "people.db" database
