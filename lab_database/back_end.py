import datetime
import pandas as pd
from peewee import *
from filt_switch import FiltSwitch

db = SqliteDatabase('./subjects.db')

class Subject(Model):
    first = CharField(null=True)
    last = CharField(null=True)
    sub_ID = IntegerField()
    year_of_birth = IntegerField(null=True)
    dominant_hand = FixedCharField(null=True)
    mail = CharField(null=True)
    subj_notes = CharField(null=True)
    send_mails = BooleanField(null=True)
    reading_span = IntegerField(null=True)
    gender = CharField(null=True)
    hebrew_age = IntegerField(null=True)
    other_languages = CharField(null=True)

    class Meta:
        database = db # This model uses the "subjects.db" database.


class Experiment(Model):
    subject = ForeignKeyField(Subject, backref='experiments')
    sub_code = CharField(null=True)
    name = CharField()
    date = DateTimeField(null=True)
    participated = BooleanField(null=True)
    exp_notes = CharField(null=True)
    exp_list = CharField(null=True)

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


def unique_experiments():
    return list(set([exp.name for exp in Experiment.select()]))

def get_table_subjects():
    query = Subject.select().dicts()
    data_dict = {}
    for row in query:
        for key,val in row.items():
            data_dict.setdefault(key, []).append(val)
    return pd.DataFrame.from_dict(data_dict).drop(columns=['id'])

def find_subject(identifier):
    df = get_table_subjects()
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
    _, is_in = find_subject(dict_new_exp['sub_ID'])
    if not is_in:
        insert_or_update_sub({'first':'', 'last':'', 'sub_ID':dict_new_exp['sub_ID'],
                              'year_of_birth':0,'dominant_hand':'','mail':'','notes':''})
    # match the internal identifier of the subject between the tables.
    sub_dict = {}
    query = Subject.select().where(Subject.sub_ID == dict_new_exp['sub_ID']).dicts()
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
    return pd.DataFrame.from_dict(data_dict).drop(columns=['id'])

"""
def participated_in():
    df = get_table_experiment()
    df = pd.DataFrame()
    for subject in df['sub_ID'].unique():
        sub_df = df.loc[df['sub_ID' == ]]
"""

def filt(filt_dict, exp_list = 0):
    if exp_list == 1: # If experiment list is requested, return a df that includes the fields specific for this experiment.
        df = get_table_experiment()
        df = df.loc[df['name'] == filt_dict['exp_include'][0]]
        for key, val in filt_dict.items():
            df = FiltSwitch().filter_by_key(key, val, df)
        ### need to add exclude by experiment

    else:
        exp = get_table_experiment()
        df = get_table_subjects()

        #now = datetime.datetime.now()
        #this_year = now.year

        # Exclude based on parameters other than exclusion/inclusion of experiments.
        for key, val in filt_dict.items():
            df = FiltSwitch().filter_by_key(key, val, df)


        for subject in df['sub_ID'].values:
            sub_exp = exp.loc[exp['sub_ID'] == subject]
            sub_exp = sub_exp['name'].values

            # Exclude by experiments
            if 'exp_exclude' in filt_dict:
                for val in filt_dict['exp_exclude']:
                    if val in sub_exp:
                        df = df.loc[df['sub_ID' != subject]]

            # Include by experiments
            if 'exp_include' in filt_dict:
                for val in filt_dict['exp_include']:
                    if (val in sub_exp) == False:
                        df = df.loc[df['sub_ID' != subject]]
    return df


def experiment_tomorrow_mails():
    df_exp = get_table_experiment()
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    df_exp.loc[df_exp['date'] == tomorrow]
    emails = []
    subs = get_table_subjects()
    sub_id = subs['sub_ID']
    for id in df_exp['sub_ID']:
        ind = sub_id == id
        emails.append(subs.loc[ind]['mail'].to_string(index=False))
    return emails


db.close()
