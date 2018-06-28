import yagmail
import json
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
#import GUI
from back_end import *

# start(GUIapp)


with open("config.json", "r") as file:
    data = json.load(file)
username = data['gmail_username']
reminder_time = data['reminder_time']

yag = yagmail.SMTP(username)


# email reminders
def mail_reminders():
    to = experiment_tomorrow_mails()
    subject_reminder = "תזכורת לניסוי"
    body_reminder = """This is a reminder
    you have an experiment tomorrow
    thanks"""
    yag.send(to=to, subject=subject_reminder, contents=body_reminder)


# new experiment announcement
def exp_mail(sub_df):
    email_list = sub_df['mail'].tolist()
    subject_new = "ניסוי חדש!"
    body_new = """אתם מוזמנים להשתתף בניסוי חדש
    תודה"""
    yag.send(to=email_list, subject=subject_new, contents=body_new)


scheduler = BlockingScheduler()
job = scheduler.add_job(mail_reminders(), 'cron', hour=reminder_time)
#scheduler.start()
