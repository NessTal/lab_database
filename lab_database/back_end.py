import sqlite3
import time
import datetime
#import faker
import peewee
from datetime import date

from peewee import *

db = SqliteDatabase('/Users/ranigera/Google Drive TAU/Advanced Python/lab_database/lab_database/subjects.db')

class Subject(Model):
    first = CharField()
    last = CharField()
    sub_ID = IntegerField()
    year_of_birth = IntegerField()
    dominant_hand = FixedCharField(max_length=1)
    mail = CharField()
    notes = CharField()
    # send_mails = BooleanField()
    # reading_span = IntegerField()
    # gender = CharField()

    class Meta:
        database = db # This model uses the "subjects.db" database.


class Experiment(Model):
    subject = ForeignKeyField(Subject, backref='experiments')
    # sub_code = CharField()
    name = CharField()
    date = DateTimeField()
    participated = BooleanField()
    # notes = CharField()
    # exp_list = CharField()

    class Meta:
        database = db # this model uses the "subjects.db" database


db.connect()
db.create_tables([Subject, Experiment])

def insert_or_update_sub(dict_new_sub):
    #check if subject exist:
    query = Subject.select().where(Subject.sub_ID == dict_new_sub['sub_ID'])
    if query.exists():
        sub = Subject.select().where(Subject.sub_ID == dict_new_sub['sub_ID']).get()
        for key, val in dict_new_sub.items():
            setattr(sub, key, val)
        sub.save()
        print('updated')
    else:
        print('new_one')
        Subject.create(**dict_new_sub).save()

for sub in Subject.select():
    print(sub.sub_ID)

query = Subject.select().order_by(Category.name)

print(sub.first, sub.last, sub.sub_ID)
    print(a)
    sub = Subject.select().where(Subject.sub_ID == id).get()
    sub = Subject.select().where(Subject.sub_ID == 010101010).get()

    Subject(first = CharField(), last = CharField(), sub_ID = IntegerField(), year_of_birth = IntegerField(),
            dominant_hand = FixedCharField(max_length=1) ,mail = CharField() ,notes = CharField()



        c.execute("INSERT INTO participants VALUES (:first,:last,:withfloat,:withint)",
                  {'first': sub.first, 'last': sub.last, 'withfloat': sub.withfloat, 'withint': sub.withint})


def update_fields(id, update_target):
    sub = Subject.select().where(Subject.sub_ID == id).get()
    field_to_update=list(update_target.keys())[0]
    update_to = update_target[field_to_update]
    setattr(sub, field_to_update, update_to)
    sub.save()



    field =

    getattr(sub,field_to_update)


#editing
sub6.name = 'MyNaMeWasUpDaTeD' #can change the inherited, everything...
sub6.save()  # Update grandma's name in the database.
# Returns: 1
#  when you call save the number of rows modified is returned.

Subject.create(first='Specialush', last='WoW', sub_ID = 123123123, year_of_birth=2000,
               dominant_hand = 'R', mail = 'aaa@bbb', notes= 'A GeNeRaL NoTe').save()

# create experiments
HRS = Experiment.create(subject=sub2, name='HRS', date='04-04-2018', participated=1)
RCC = Experiment.create(subject=sub3, name='RCC', date='05-04-2018', participated=0)
BOOST = Experiment.create(subject=sub4, name='BOOST', date='08-04-2018', participated=1)
BSV = Experiment.create(subject=sub5, name='BSV',date='01-04-2018', participated=0)

#remove a subject:
BOOST.delete_instance() # he had a great life
# Returns: 1. The return value of delete_instance() is the number of rows removed from the database.

#------- Retrieving data------
subjush = Subject.select().where(Subject.first == 'BOBO').get()
# A shorter alternative:
subjush = Subject.get(Subject.first == 'BOBO')
subjush = Subject.get(Subject.sub_ID == 123123123)

for sub in Subject.select():
    print(sub.sub_ID)
a = [sub.first for sub in Subject.select()]
a = [sub for sub in Subject.select()]
#### TASK --> make it a table in pandas

# listing the experiments with their subjects
query = Experiment.select().where(Experiment.name == 'BSV')
for exp in query:
    print(exp.name, exp.subject.first)

#We can avoid the extra queries by selecting both Pet and Person, and adding a join.
#The right way...
query = Experiment.select(Experiment, Subject).join(Subject).where(Experiment.name == 'BSV')

for exp in query:
    print(exp.name, exp.subject.first)

# Let’s get all the experiment conducted by a specific subject:
for exp in Experiment.select().join(Subject).where(Subject.first == 'ZOLO'):
    print(exp.name)
# An alternative... with a specific instance... not sure it is better for me...
for exp in Experiment.select().where(Experiment.subject == sub2):
    print(exp.name)
# can add an orderby()... something



#Usually this type of duplication is undesirable. To accommodate the more common (and intuitive) workflow of listing a person and attaching a list of that person’s pets, we can use a special method called prefetch():

query = Subject.select().order_by(Subject.first).prefetch(Experiment)
for subject in query:
    print(subject.first)
    for exp in subject.experiments:
        print('  *', exp.name)



# One last query. This will use a SQL function to find all people whose names start with either an upper or lower-case G:
expression = fn.Lower(fn.Substr(Person.name, 1, 1)) == 'g'
for person in Person.select().where(expression):
    print(person.name)


db.close()






# older
def update_field(id, update_target):
    sub = Subject.select().where(Subject.sub_ID == id).get()
    field_to_update=list(update_target.keys())[0]
    update_to = update_target[field_to_update]
    setattr(sub, field_to_update, update_to)
    sub.save()
