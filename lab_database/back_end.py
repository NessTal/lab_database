import datetime
import pandas as pd
from peewee import *

db = SqliteDatabase(r'./subjects.db')

class Subject(Model):
    first = CharField()
    last = CharField()
    sub_ID = IntegerField()
    year_of_birth = IntegerField()
    dominant_hand = FixedCharField(max_length=1)
    mail = CharField()
    notes = CharField()
    send_mails = BooleanField()
    reading_span = IntegerField()
    gender = CharField()
    hebrew_age = IntegerField()
    other_languages = CharField()

    class Meta:
        database = db # This model uses the "subjects.db" database.


class Experiment(Model):
    subject = ForeignKeyField(Subject, backref='experiments')
    sub_code = CharField()
    name = CharField()
    date = DateTimeField()
    participated = BooleanField()
    notes = CharField()
    exp_list = CharField()

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

def unique_exoeriments():
    return list(set([exp.name for exp in Experiment.select()]))

def get_table_subjects():
    query = Subject.select().dicts()
    data_dict = {}
    for row in query:
        for key,val in row.items():
            data_dict.setdefault(key, []).append(val)
    return pd.DataFrame.from_dict(data_dict).drop(columns=['id'])

def find_subject(identifier):
    df = get_table_subjects
    if ' ' in str(identifier):
        first_name, last_name = identifier.split(" ", 1)
        sub = df.loc[(df['first'] == first_name) & (df['last'] == last_name)]
    else:
        if type(identifier) == str:
            sub = df.loc[df['mail'] == identifier]
        else:
            sub = df.loc[df['sub_ID'] == identifier]
            if not sub.empty:
                return sub, not sub.empty
    return sub, not sub.empty

def insert_experiment(dict_new_exp):
    # check if the subject is in Subject data base and add if needed:
    _, is_in = find_subject(dict_new_exp['subject'])
    if not is_in:
        insert_or_update_sub({'first':'', 'last':'', 'sub_ID':dict_new_exp['subject'],
                              'year_of_birth':0,'dominant_hand':'','mail':'','notes':''})
    # match the internal identifier of the subject between the tables.
    sub_dict = {}
    query = Subject.select().where(Subject.sub_ID == dict_new_exp['subject']).dicts()
    for row in query:
        for key,val in row.items():
            print(key,val)
            sub_dict.setdefault(key, []).append(val)
    # assign the new raw to the table
    dict_new_exp['subject'] = sub_dict['id'][0]
    Experiment.create(**dict_new_exp).save()

def get_table_experiment():
    query = Experiment.select(Experiment, Subject).join(Subject).dicts()
    data_dict = {}
    for row in query:
        for key,val in row.items():
            data_dict.setdefault(key, []).append(val)
    return pd.DataFrame.from_dict(data_dict).drop(columns=['id','subject'])


def filt(filt_dict):
    df_exp = get_table_experiment()
    #If one experiment is given, just return all the data of this experiment.
    if len(filt_dict['exp_include']) == 1:
        return df_exp.loc[df_exp['name'] == filt_dict['exp_include'][0]]
    else:
        #define some relevant stuff for the age-based exclusion:
        now = datetime.datetime.now()
        this_year = now.year
        max_year = this_year - int(filt_dict['year_from'])
        min_year = this_year - int(filt_dict['year_to'])
        # Exclude based on parameters other than exclusion/inclusion of experiments.
        sub = df_exp.loc[(df_exp['gender'] == filt_dict['gender']) & (df_exp['year_of_birth'] >= min_year) & (df_exp['year_of_birth'] <= max_year) &
                         (df_exp['dominant_hand'] == filt_dict['hand']) & (df_exp['reading_span'] >= filt_dict['rs_from']) & (df_exp['reading_span'] <= filt_dict['rs_to'])]
        # Exclude by other experiments
        if filt_dict['exp_exclude']:
            for val in filt_dict['exp_exclude']:
                sub = sub.loc[df_exp['name'] != val]
        # Include by experiments (only if exclusion by experiment was entered)
        elif filt_dict['exp_include']:
            for val in filt_dict['exp_include']:
                sub = sub.loc[df_exp['name'] == val]
        return sub

def experiment_tomorrow_mails():
    df_exp = get_table_experiment()
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    return df_exp.loc[df_exp['date'] == tomorrow]


db.close()


