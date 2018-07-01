from back_end import *

dict = {'sub_ID': 7,                # necessary
        'name': 'exp4',             # necessary
        'first': 'A',
        'last': 'B',
        'year_of_birth': 2000,
        'dominant_hand': 'Left',
        'mail': 'abc@mail.com',
        'subj_notes': 'adklm',
        'send_mails': False,
        'reading_span': 5,
        'gender': 'Male',
        'hebrew_age': 0,
        'other_languages': 'English',
        'date':'1/1/1',
        'sub_code': '5',
        'participated': True,
        'exp_list':'A',
        'exp_notes':'sxwdw'
}
add_or_update(dict)

print(get_table_experiment())
print(get_table_subjects())
