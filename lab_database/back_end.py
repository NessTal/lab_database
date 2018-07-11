import datetime
import pandas as pd
# from peewee import *
from playhouse.migrate import *
from filt_switch import FiltSwitch

db = SqliteDatabase('./subjects.db')

subject_fields = ['first_name', 'last_name','subject_ID','year_of_birth','dominant_hand','mail','subject_notes',
                  'send_mails','reading_span','gender','hebrew_age','other_languages']
experiment_fields = ['participant_number','experiment','date','participated','experiment_notes','exp_list']

col_order_subjects = ['first_name', 'last_name','subject_ID','mail','year_of_birth','gender','hebrew_age','other_languages',
                      'dominant_hand','reading_span','subject_notes','send_mails']
col_order_experiment = ['experiment','participant_number','exp_list','date','first_name', 'last_name','subject_ID','mail','year_of_birth','gender',
                        'hebrew_age','other_languages','dominant_hand','reading_span','subject_notes','experiment_notes',
                        'participated','send_mails']


class Subject(Model):
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    subject_ID = IntegerField()
    year_of_birth = IntegerField(null=True)
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
    subject = ForeignKeyField(Subject, backref='experiments')
    participant_number = CharField(null=True)
    experiment = CharField()
    date = DateTimeField(null=True)
    participated = BooleanField(null=True)
    experiment_notes = CharField(null=True)
    exp_list = CharField(null=True)

    class Meta:
        database = db # this model uses the "subjects.db" database


db.connect()
db.create_tables([Subject, Experiment])


def add_new_fields_to_tables():
    df = pd.read_csv('added_fields.csv')
    for idx, row in df.iterrows():
        field_name = row['field_name']
        table_name = row['table_name']
        if row['field_type'] == 'integer':
            exec(table_name + '._meta.add_field(field_name,FloatField(null=True))')
        if row['field_type'] == 'boolean':
            exec(table_name + '._meta.add_field(field_name,BooleanField(null=True))')
        if row['field_type'] == 'date':
            exec(table_name + '._meta.add_field(field_name,DateField(null=True))')
        if row['field_type'] == 'text':
            exec(table_name + '._meta.add_field(field_name,CharField(null=True))')

        if table_name == 'Experiment':
            experiment_fields.append(field_name)
            col_order_experiment.append(field_name)
        else:
            subject_fields.append(field_name)
            col_order_subjects.append(field_name)
            col_order_experiment.append(field_name)


add_new_fields_to_tables()

def unique_experiments():
    exp_list = list(set([exp.experiment for exp in Experiment.select()]))
    exp_list.sort(key=str.lower)
    return exp_list


def get_table_subjects():
    query = Subject.select().dicts()
    data_dict = {}
    for row in query:
        for key,val in row.items():
            data_dict.setdefault(key, []).append(val)
    df = pd.DataFrame.from_dict(data_dict).drop(columns=['id'])
    df = df[col_order_subjects]
    #df.loc[df['year_of_birth'].astype(str).values == 'nan','year_of_birth'] = 0
    #df['year_of_birth'] = df['year_of_birth'].astype(int)
    #df['year_of_birth'] = df['year_of_birth'].astype(str)
    #df.loc[df['year_of_birth'] == '0','year_of_birth'] = 'None'
    #df.loc[df['reading_span'].astype(str).values == 'nan','reading_span'] = 0
    #df.loc[df['reading_span'].astype(str).values == 'None','reading_span'] = 0
    #df['reading_span'] = df['reading_span'].astype(int)
    #df['reading_span'] = df['reading_span'].astype(str)
    #df.loc[df['reading_span'] == '0','reading_span'] = 'None'
    return df


def get_table_experiment():
    query = Experiment.select(Experiment, Subject).join(Subject).dicts()
    data_dict = {}
    for row in query:
        for key,val in row.items():
            data_dict.setdefault(key, []).append(val)
    df = pd.DataFrame.from_dict(data_dict).drop(columns=['id'])
    df = df[col_order_experiment]
    sub_exp_dict = {}
    return df

class Tables:
    def __init__(self):
        self.table_subjects = get_table_subjects()
        self.table_experiment = get_table_experiment()

tables = Tables()

def devide_dict(dict):
    exp_dict = {}
    sub_dict = {}
    for key, val in dict.items():
        if key in experiment_fields:
            exp_dict[key] = val
        else:
            sub_dict[key] = val
    return sub_dict, exp_dict


def get_if_exists(identifier, experiment = None):
    output = False
    if ' ' in str(identifier):
        first, last = identifier.split(" ", 1)
        sub = Subject.select().where((Subject.first_name == first) & (Subject.last_name == last))
    else:
        if '@' in str(identifier):
            sub = Subject.select().where(Subject.mail == identifier)
        else:
            sub = Subject.select().where(Subject.subject_ID == identifier)
    if sub.count() > 1:
        output = 'Too many!'
    elif sub.exists():
        sub = sub.get()
        if experiment != None:
            exp = Experiment.select().where((Experiment.subject == sub) & (Experiment.experiment == experiment))
            if exp.exists():
                exp = exp.get()
                exp_table = tables.table_experiment
                output = exp_table.loc[list(exp_table['subject_ID'] == sub.subject_ID)]  #####
                output = output.loc[list(output['experiment'] == exp.experiment)]
        if type(output) != pd.DataFrame:
            sub_table = tables.table_subjects
            output = sub_table.loc[sub_table['subject_ID'] == sub.subject_ID]  #####
    return output


def add_or_update(dict):
    sub_dict,exp_dict = devide_dict(dict)
    sub = Subject.select().where(Subject.subject_ID == sub_dict['subject_ID'])  #####
    if sub.exists() == False:
        sub = Subject.create(**sub_dict)
        sub.save()
        exp_dict['subject'] = sub
        if 'experiment' in list(exp_dict.keys()):
            Experiment.create(**exp_dict).save()
    else:
        sub = sub.get()
        for key, val in sub_dict.items():
            setattr(sub, key, val)
        sub.save()
        if 'experiment' in list(exp_dict.keys()):
            exp = Experiment.select().where((Experiment.subject == sub) & (Experiment.experiment == exp_dict['experiment']))
            if exp.exists():
                exp = exp.get()
                for key, val in exp_dict.items():
                    setattr(exp, key, val)
                exp.save()
            else:
                exp_dict['subject'] = sub
                Experiment.create(**exp_dict).save()
            tables.table_experiment = get_table_experiment()
    tables.table_subjects = get_table_subjects()
    export_all_to_csv()


def filt(filt_dict, exp_list = 0):
    exp = tables.table_experiment
    sub = tables.table_subjects

    # Exclude based on parameters other than exclusion/inclusion of experiments.
    for key, val in filt_dict.items():
        sub = FiltSwitch().filter_by_key(key, val, sub)

    for subject in sub['subject_ID'].values:  #####
        sub_exp = exp.loc[exp['subject_ID'] == subject]  #####
        sub_exp = sub_exp['experiment'].values

        # Exclude by experiments
        if 'exp_exclude' in filt_dict:
            for val in filt_dict['exp_exclude']:
                if val in sub_exp:
                    sub = sub.loc[sub['subject_ID'] != subject]  #####

        if exp_list == 0:
            # Include by experiments
            if 'exp_include' in filt_dict:
                for val in filt_dict['exp_include']:
                    if (val in sub_exp) == False:
                        sub = sub.loc[sub['subject_ID'] != subject]  #####

    if exp_list == 1:  # If an experiment list was requested, return a df that includes the fields specific for this experiment.
        exp = exp.loc[exp['experiment'] == filt_dict['exp_include'][0]]
        result = exp.loc[exp['subject_ID'].isin(sub['subject_ID'])]  #####
    else:
        result = sub
    return result


def experiment_tomorrow_mails():
    df_exp = tables.table_experiment
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow = tomorrow.strftime('%d-%m-%y')
    df_exp = df_exp.loc[df_exp['date'] == tomorrow]
    emails = df_exp['mail'].tolist()
    print(emails)
    return emails


def export_all_to_csv(*args):
    tables.table_subjects.to_csv('../exported files/all_subjects_db.csv', index=False)
    tables.table_experiment.to_csv('../exported files/all_experiments_db.csv', index=False)


def import_from_excel(file):
    df = pd.read_csv(file, encoding='hebrew')
    dict = df.to_dict(orient = 'list')
    #dict['date'] = [datetime.datetime.strptime(date, '%d-%m-%y').date() for date in dict['date']]
    row_num = 0
    for row in dict['subject_ID']:  #####
        row_dict = {}
        for key, list in dict.items():
            if str(list[row_num]) != 'nan':
                row_dict[key] = list[row_num]
        add_or_update(row_dict)
        row_num += 1
    tables.table_subjects = get_table_subjects()
    tables.table_experiment = get_table_experiment()
    export_all_to_csv()


def add_new_field(table_name,field_name,field_type):
    dict = {'integer': FloatField(null=True), 'boolean': BooleanField(null=True), 'date': DateField(null=True), 'text': CharField(null=True)}
    field = dict[field_type]

    migrator = SqliteMigrator(db)
    migrate(migrator.add_column(table_name,field_name,field))

    if field_type == 'integer':
        exec(table_name + '._meta.add_field(field_name,IntegerField(null=True))')
    if field_type == 'boolean':
        exec(table_name + '._meta.add_field(field_name,BooleanField(null=True))')
    if field_type == 'date':
        exec(table_name + '._meta.add_field(field_name,DateField(null=True))')
    if field_type == 'text':
        exec(table_name + '._meta.add_field(field_name,CharField(null=True))')

    subject_fields.append(field_name)
    col_order_subjects.append(field_name)
    col_order_experiment.append(field_name)

    tables.table_subjects = get_table_subjects()
    tables.table_experiment = get_table_experiment()


db.close()

