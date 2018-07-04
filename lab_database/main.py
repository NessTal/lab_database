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
    to = experiment_tomorrow_mails()
    subject_reminder = "תזכורת לניסוי"
    body_reminder = """היי,
    זאת תזכורת לכך שקבענו ניסוי למחר, בבניין ווב חדר 202.
    נתראה!
    """
    body_reminder = '<div align="right">'+body_reminder+'</div>'
    print(to)
    yag.send(bcc=to, subject=subject_reminder, contents=body_reminder)


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


