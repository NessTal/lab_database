import yagmail
import json
from back_end import *

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
    df = experiment_tomorrow_mails()

    to = df['mail'].to_list()
    time = df['scheduled_time'].to_list()
    location = df['location'].to_list()
    experimenter = df['experimenter_name'].to_list()

    title = "תזכורת להשתתפות בניסוי (של {experimenter})"
    body = """היי,
    זאת תזכורת לניסוי שקבענו למחר. ניפגש בשעה {time} בבניין {place}.
    נתראה!
    {experimentr}
    """

    idx = 0
    for mail in to:
        title.format(experimenter=experimenter[idx])
        body = '<div align="right">'+body.format(experimenter=experimenter[idx], time=time[idx], location=location[idx])+'</div>'
        yag.send(bcc=mail, subject=title, contents=body)
        idx += 1



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


