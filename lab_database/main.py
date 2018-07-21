import yagmail
import json
#from back_end import *
from get_from_calendar import *


with open("config.json", "r") as file:
    data = json.load(file)
username = data['gmail_username']
password = data['gmail_password']
reminder_time = data['reminder_time']

import_path = data['import_path']
export_path = data['export_path']

max_range_value = data['max_range_value']

yag = yagmail.SMTP(username, password)


# email reminders
def mail_reminders():
    calender_to_db()

    df = experiment_tomorrow_mails()

    to = df['mail'].tolist()
    time = df['scheduled_time'].tolist()
    location = df['location'].tolist()
    experimenter = df['experimenter_name'].tolist()

    title = "תזכורת להשתתפות בניסוי (של {experimenter})"
    body = """היי,
    זאת תזכורת לניסוי שקבענו למחר. ניפגש בשעה {time} בבניין {location}.
    נתראה!
    {experimenter}
    """

    idx = 0
    for mail in to:
        current_title = title.format(experimenter=experimenter[idx])
        current_body = '<div dir="rtl">'+body.format(experimenter=experimenter[idx], time=time[idx], location=location[idx])+'</div>'
        yag.send(bcc=mail, subject=current_title, contents=current_body)
        idx += 1

mail_reminders()

# new experiment announcement
def exp_mail(emails_list,subject='',contents=''):
    if subject == '':
        subject = "ניסוי חדש!"
    if contents == '':
        contents = """יש לנו ניסוי חדש במעבדה, ונשמח אם תרצו להשתתף בו.
        במידה ואתם מעוניינים, פנו אלינו לפרטים נוספים.
        תודה"""
    contents = '<div align="right">'+contents+'</div>'
    yag.send(bcc=emails_list, subject=subject, contents=contents)


