import datetime
import pandas as pd
# from peewee import *
from playhouse.migrate import *
from filt_switch import FiltSwitch

db = SqliteDatabase('./subjects.db')


subject_fields = ['first_name','last_name','subject_ID','mail','date_of_birth','gender','hebrew_age','other_languages',
                  'dominant_hand','reading_span','subject_notes','send_mails']
experiment_fields = ['experiment_name','experimenter_name','experimenter_mail','lab', 'duration','location','fields','key_words','description']
session_default_fields_before = ['experiment_name','participant_number','exp_list','date']
session_default_fields_after = ['participated','session_notes']
session_optional_fields = ['scheduled_time', 'credit']


class Subject(Model):
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    subject_ID = IntegerField()
    date_of_birth = CharField(null=True)
    dominant_hand = FixedCharField(null=True)
    mail = CharField(null=True)
    subject_notes = CharField(null=True)
    send_mails = BooleanField(null=True)
    reading_span = IntegerField(null=True)
    gender = CharField(null=True)
    hebrew_age = FloatField(null=True)
    other_languages = CharField(null=True)

    class Meta:
        database = db # This model uses the "subjects.db" database.

class Experiment(Model):
    experiment_name = CharField()
    experimenter_name = CharField(null=True)
    experimenter_mail = CharField(null=True)
    duration = IntegerField(null=True)
    description = CharField(null=True)
    fields = CharField(null=True)
    key_words = CharField(null=True)
    lab = CharField(null=True)
    location = CharField(null=True)

    class Meta:
        database = db # This model uses the "subjects.db" database.

class Session(Model):
    subject = ForeignKeyField(Subject, backref='experiments')
    experiment = ForeignKeyField(Experiment, backref='participants')
    participant_number = CharField(null=True)
    date = CharField(null=True)
    participated = BooleanField(null=True)
    session_notes = CharField(null=True)
    exp_list = CharField(null=True)
    scheduled_time = CharField(null=True)
    credit = BooleanField(null=True)

    class Meta:
        database = db # this model uses the "subjects.db" database


db.connect()
db.create_tables([Subject, Experiment,Session])


def add_new_fields_to_tables():
    df = pd.read_csv('added_fields.csv')
    for idx, row in df.iterrows():
        field_name = row['field_name']
        table_name = row['table_name']
        if row['field_type'] == 'integer':
            exec(table_name + '._meta.add_field(field_name,FloatField(null=True))')
        if row['field_type'] == 'boolean':
            exec(table_name + '._meta.add_field(field_name,BooleanField(null=True))')
        else:
            exec(table_name + '._meta.add_field(field_name,CharField(null=True))')

        if table_name == 'Subject':
            subject_fields.append(field_name)
        elif table_name == 'Experiment':
            experiment_fields.append(field_name)
        else:
            session_optional_fields.append(field_name)

add_new_fields_to_tables()

def unique_experiments():
    exp_list = list(set([exp.experiment_name for exp in Experiment.select()]))
    exp_list.sort(key=str.lower)
    return exp_list


def get_table_subjects():
    query = Subject.select().dicts()
    data_dict = {}
    for row in query:
        for key,val in row.items():
            data_dict.setdefault(key, []).append(val)
    df = pd.DataFrame.from_dict(data_dict).drop(columns=['id'])
    df = df[subject_fields]
    return df

def get_table_experiments():
    query = Experiment.select().dicts()
    data_dict = {}
    for row in query:
        for key,val in row.items():
            data_dict.setdefault(key, []).append(val)
    df = pd.DataFrame.from_dict(data_dict).drop(columns=['id'])
    df = df[experiment_fields]
    return df

def get_table_sessions():
    query = Session.select(Session, Experiment, Subject).join(Experiment).switch(Session).join(Subject).dicts()
    data_dict = {}
    for row in query:
        for key,val in row.items():
            data_dict.setdefault(key, []).append(val)
    df = pd.DataFrame.from_dict(data_dict).drop(columns=['id'])
    df = df[session_default_fields_before + subject_fields + session_default_fields_after +
            session_optional_fields + experiment_fields[1:]]
    return df

class Tables:
    def __init__(self):
        self.table_subjects = get_table_subjects()
        self.table_experiments = get_table_experiments()
        self.table_for_emails = get_table_sessions()
        self.table_sessions = self.table_for_emails[session_default_fields_before + subject_fields +
                                                    session_default_fields_after + session_optional_fields]

# use when creating the db for the first time:
"""
sub1 = Subject.create(subject_ID = 1)
exp1 = Experiment.create(experiment_name = 'exp1')
ses1 = Session.create(subject = sub1, experiment = exp1)
"""

tables = Tables()

def devide_dict(dict):
    sub_dict = {}
    exp_dict = {}
    ses_dict = {}
    for key, val in dict.items():
        if key in subject_fields:
            sub_dict[key] = val
        elif key in experiment_fields:
            exp_dict[key] = val
        else:
            ses_dict[key] = val
    return sub_dict, exp_dict, ses_dict


def get_if_exists(identifier, experiment = None):
    output = False
    if ' ' in str(identifier):
        first, last = identifier.split(" ", 1)
        sub = tables.table_subjects.loc[(tables.table_subjects['first_name'] == first) & (tables.table_subjects['last_name'] == last)]
    else:
        if '@' in str(identifier):
            sub = tables.table_subjects.loc[tables.table_subjects['mail'] == identifier]
        else:
            sub = tables.table_subjects.loc[tables.table_subjects['subject_ID'] == identifier]
    if len(sub) > 1:
        output = 'Too many!'
    elif len(sub) == 1:
        output = sub
        if experiment != None:
            ses = tables.table_sessions.loc[(tables.table_sessions['subject_ID'] == sub['subject_ID'].values[0]) &
                                            (tables.table_sessions['experiment_name'] == experiment)]
            if len(ses) == 1:
                exp_fields = tables.table_experiments.loc[tables.table_experiments['experiment_name'] == experiment]
                exp_fields = exp_fields['fields'].values[0].split(', ')
                output = ses[session_default_fields_before + subject_fields + session_default_fields_after +
                             exp_fields]
    return output


def add_or_update(dict):
    sub_dict, exp_dict, ses_dict = devide_dict(dict)
    sub = Subject.select().where(Subject.subject_ID == sub_dict['subject_ID'])
    if sub.exists() == False:
        sub = Subject.create(**sub_dict)
        sub.save()
        exp_dict['subject'] = sub
        if 'experiment_name' in list(exp_dict.keys()):
            exp = Experiment.select().where(Experiment.experiment_name == exp_dict['experiment_name']).get()
            ses_dict['subject'] = sub
            ses_dict['experiment'] = exp
            ses = Session.create(**ses_dict)
            ses.save()
    else:
        sub = sub.get()
        for key, val in sub_dict.items():
            setattr(sub, key, val)
        sub.save()
        if 'experiment_name' in list(exp_dict.keys()):
            exp = Experiment.select().where(Experiment.experiment_name == exp_dict['experiment_name']).get()
            ses = Session.select().where((Session.subject == sub) & (Session.experiment == exp))
            if ses.exists():
                ses = ses.get()
                for key, val in ses_dict.items():
                    setattr(ses, key, val)
                ses.save()
            else:
                ses_dict['subject'] = sub
                ses_dict['experiment'] = exp
                Session.create(**ses_dict).save()
            tables.table_for_emails = get_table_sessions()
            tables.table_sessions = tables.table_for_emails[session_default_fields_before + subject_fields +
                                                            session_default_fields_after + session_optional_fields]
    tables.table_subjects = get_table_subjects()
    export_all_to_csv()


def get_experiment(experiment_name):
    exp = tables.table_experiments.loc[tables.table_experiments['experiment_name'] == experiment_name]
    return exp


def add_or_update_experiment(dict):
    exp = Experiment.select().where(Experiment.experiment_name == dict['experiment_name'])
    dict1 = dict.copy()
    for key, val in dict1.items():
        if (val == '') or (val == 'None') or (val == 'nan'):
            dict.pop(key)

    if exp.exists() == False:
        exp = Experiment.create(**dict)
        exp.save()
    else:
        exp = exp.get()
        for key, val in dict.items():
            setattr(exp, key, val)
        exp.save()
    tables.table_experiments = get_table_experiments()
    export_all_to_csv()


def filt(filt_dict, exp_list = 0):
    sub = tables.table_subjects
    ses = tables.table_sessions

    # Exclude based on parameters other than experiments.
    for key, val in filt_dict.items():
        sub = FiltSwitch().filter_by_key(key, val, sub)

    for subject in sub['subject_ID'].values:
        sub_exp = ses.loc[ses['subject_ID'] == subject]
        sub_exp = sub_exp['experiment_name'].values

        # Exclude by experiments
        if 'exp_exclude' in filt_dict:
            for val in filt_dict['exp_exclude']:
                if val in sub_exp:
                    sub = sub.loc[sub['subject_ID'] != subject]

        if exp_list == 0:
            # Include by experiments
            if 'exp_include' in filt_dict:
                for val in filt_dict['exp_include']:
                    if (val in sub_exp) == False:
                        sub = sub.loc[sub['subject_ID'] != subject]

    if exp_list == 1:  # If an experiment list was requested, return a df that includes the fields specific for this experiment.
        ses = ses.loc[ses['experiment_name'] == filt_dict['exp_include'][0]]
        ses = ses.loc[ses['subject_ID'].isin(sub['subject_ID'])]
        exp_fields = tables.table_experiments.loc[tables.table_experiments['experiment_name'] == filt_dict['exp_include'][0]]
        if exp_fields['fields'].values[0] != None:
            exp_fields = exp_fields['fields'].values[0].split(', ')
            result = ses[session_default_fields_before + subject_fields + session_default_fields_after + exp_fields]
        else:
            result = ses[session_default_fields_before + subject_fields + session_default_fields_after]
    else:
        result = sub
    return result

def filt_experiments(filt_exp_dict):
    result = tables.table_experiments
    if 'key_words' in filt_exp_dict.keys():
        for key_word in filt_exp_dict.pop('key_words'):
            result = result.loc[result['key_words'].str.contains(key_word) == True]
    for key, val in filt_exp_dict.items():
        result = FiltSwitch().filter_by_key(key, val, result)
    return result

def experiment_tomorrow_mails():
    df_ses = tables.table_for_emails
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow = tomorrow.strftime('%d-%m-%Y')
    df_ses = df_ses.loc[df_ses['date'] == tomorrow]
    emails = df_ses['mail'].tolist()
    print(emails)
    return df_ses

def export_all_to_csv(*args):
    tables.table_subjects.to_csv('../exported files/all_subjects_db.csv', index=False)
    tables.table_experiments.to_csv('../exported files/all_experiments_db.csv', index=False)
    tables.table_sessions.to_csv('../exported files/all_sessions_db.csv', index=False)


def import_from_excel(file,date_fields):
    df = pd.read_csv(file, encoding='hebrew', parse_dates=False)
    for d_field in date_fields:
        df[d_field] = df[d_field+'_dd'].astype(str) + '-' + df[d_field+'_mm'].astype(str) + '-' + df[d_field+'_yyyy'].astype(str)
        df = df.drop(columns=[d_field+'_dd',d_field+'_mm',d_field+'_yyyy'])
    dict = df.to_dict(orient = 'list')
    #dict['date'] = [datetime.datetime.strptime(date, '%d-%m-%y').date() for date in dict['date']]
    row_num = 0
    for row in dict['subject_ID']:
        row_dict = {}
        for key, vals in dict.items():
            val = vals[row_num]
            if str(val) != 'nan':
                row_dict[key] = val
        add_or_update(row_dict)
        row_num += 1
    tables.table_subjects = get_table_subjects()
    tables.table_for_emails = get_table_sessions()
    tables.table_sessions = tables.table_for_emails[session_default_fields_before + subject_fields +
                                                    session_default_fields_after + session_optional_fields]
    export_all_to_csv()


def add_new_field(table_name,field_name,field_type):
    dict = {'integer': FloatField(null=True), 'boolean': BooleanField(null=True), 'date': CharField(null=True), 'text': CharField(null=True)}
    field = dict[field_type]

    migrator = SqliteMigrator(db)
    migrate(migrator.add_column(table_name,field_name,field))

    if field_type == 'integer':
        exec(table_name + '._meta.add_field(field_name,FloatField(null=True))')
    elif field_type == 'boolean':
        exec(table_name + '._meta.add_field(field_name,BooleanField(null=True))')
    else:
        exec(table_name + '._meta.add_field(field_name,CharField(null=True))')

    if table_name == 'Subject':
        subject_fields.append(field_name)
    elif table_name == 'Experiment':
        experiment_fields.append(field_name)
    else:
        session_optional_fields.append(field_name)

    tables.table_subjects = get_table_subjects()
    tables.table_experiments = get_table_experiments()
    tables.table_for_emails = get_table_sessions()
    tables.table_sessions = tables.table_for_emails[session_default_fields_before + subject_fields +
                                                    session_default_fields_after + session_optional_fields]


db.close()

