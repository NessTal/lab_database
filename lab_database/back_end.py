import datetime
import pandas as pd
# from peewee import *
from playhouse.migrate import *
from filt_switch import FiltSwitch

db = SqliteDatabase('./subjects.db')

subject_fields = ['first', 'last','sub_ID','year_of_birth','dominant_hand','mail','sub_notes',
                  'send_mails','reading_span','gender','hebrew_age','other_languages']
experiment_fields = ['sub_code','exp_name','date','participated','exp_notes','exp_list']

col_order_subjects = ['first', 'last','sub_ID','mail','year_of_birth','gender','hebrew_age','other_languages',
                      'dominant_hand','reading_span','sub_notes','send_mails']
col_order_experiment = ['exp_name','sub_code','exp_list','date','first', 'last','sub_ID','mail','year_of_birth','gender',
                        'hebrew_age','other_languages','dominant_hand','reading_span','sub_notes','exp_notes',
                        'participated','send_mails']


class Subject(Model):
    first = CharField(null=True)
    last = CharField(null=True)
    sub_ID = IntegerField()
    year_of_birth = IntegerField(null=True)
    dominant_hand = FixedCharField(null=True)
    mail = CharField(null=True)
    sub_notes = CharField(null=True)
    send_mails = BooleanField(null=True)
    reading_span = IntegerField(null=True)
    gender = CharField(null=True)
    hebrew_age = IntegerField(null=True)
    other_languages = CharField(null=True)
#    new_field = IntegerField(null=True) # todo: find a way to add via code!!!

    class Meta:
        database = db # This model uses the "subjects.db" database.


class Experiment(Model):
    subject = ForeignKeyField(Subject, backref='experiments')
    sub_code = CharField(null=True)
    exp_name = CharField()
    date = DateTimeField(null=True)
    participated = BooleanField(null=True)
    exp_notes = CharField(null=True)
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
            exec(table_name + '._meta.add_field(field_name,IntegerField(null=True))')
        if row['field_type'] == 'boolean':
            exec(table_name + '._meta.add_field(field_name,BooleanField(null=True))')
        if row['field_type'] == 'date':
            exec(table_name + '._meta.add_field(field_name,DateField(null=True))')
        if row['field_type'] == 'text':
            exec(table_name + '._meta.add_field(field_name,CharField(null=True))')


def unique_experiments():
    exp_list = list(set([exp.exp_name for exp in Experiment.select()]))
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
        sub = Subject.select().where((Subject.first == first) & (Subject.last == last))
    else:
        if type(identifier) == str:
            sub = Subject.select().where(Subject.mail == identifier)
        else:
            sub = Subject.select().where(Subject.sub_ID == identifier)
    if sub.count() > 1:
        output = 'Too many!'
    elif sub.exists():
        sub = sub.get()
        if experiment != None:
            exp = Experiment.select().where((Experiment.subject == sub) & (Experiment.exp_name == experiment))
            if exp.exists():
                exp = exp.get()
                exp_table = tables.table_experiment
                output = exp_table.loc[list(exp_table['sub_ID'] == sub.sub_ID)]  #####
                output = output.loc[list(output['exp_name'] == exp.exp_name)]
        if type(output) != pd.DataFrame:
            sub_table = tables.table_subjects
            output = sub_table.loc[sub_table['sub_ID'] == sub.sub_ID]  #####
    return output


def add_or_update(dict):
    sub_dict,exp_dict = devide_dict(dict)
    sub = Subject.select().where(Subject.sub_ID == sub_dict['sub_ID'])  #####
    if sub.exists() == False:
        sub = Subject.create(**sub_dict)
        sub.save()
        exp_dict['subject'] = sub
        Experiment.create(**exp_dict).save()
    else:
        sub = sub.get()
        for key, val in sub_dict.items():
            setattr(sub, key, val)
        sub.save()
        exp = Experiment.select().where((Experiment.subject == sub) & (Experiment.exp_name == exp_dict['exp_name']))
        if exp.exists():
            exp = exp.get()
            for key, val in exp_dict.items():
                setattr(exp, key, val)
            exp.save()
        else:
            exp_dict['subject'] = sub
            Experiment.create(**exp_dict).save()
    tables.table_subjects = get_table_subjects()
    tables.table_experiment = get_table_experiment()
    export_all_to_csv()


def filt(filt_dict, exp_list = 0):
    exp = tables.table_experiment
    sub = tables.table_subjects

    # Exclude based on parameters other than exclusion/inclusion of experiments.
    for key, val in filt_dict.items():
        sub = FiltSwitch().filter_by_key(key, val, sub)

    for subject in sub['sub_ID'].values:  #####
        sub_exp = exp.loc[exp['sub_ID'] == subject]  #####
        sub_exp = sub_exp['exp_name'].values

        # Exclude by experiments
        if 'exp_exclude' in filt_dict:
            for val in filt_dict['exp_exclude']:
                if val in sub_exp:
                    sub = sub.loc[sub['sub_ID'] != subject]  #####

        if exp_list == 0:
            # Include by experiments
            if 'exp_include' in filt_dict:
                for val in filt_dict['exp_include']:
                    if (val in sub_exp) == False:
                        sub = sub.loc[sub['sub_ID'] != subject]  #####

    if exp_list == 1:  # If an experiment list was requested, return a df that includes the fields specific for this experiment.
        exp = exp.loc[exp['exp_name'] == filt_dict['exp_include'][0]]
        result = exp.loc[exp['sub_ID'].isin(sub['sub_ID'])]  #####
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
    for row in dict['sub_ID']:  #####
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
    dict = {'integer': IntegerField(null=True), 'boolean': BooleanField(null=True), 'date': DateField(null=True), 'text': CharField(null=True)}
    field = dict[field_type]

    print(table_name)
    print(field_name)
    print(field_type)

    migrator = SqliteMigrator(db)
    migrate(migrator.add_column(table_name,field_name,field))


db.close()

