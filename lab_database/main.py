import yagmail
import json
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# database

# GUI

with open("config.json", "r") as file:
    data = json.load(file)
username = data['gmail_username']
reminder_time = data['reminder_time']

yag = yagmail.SMTP(username)


# email reminders
def mail_reminders(experiment_list):
    for experiment in experiment_list:
        if experiment.date == (datetime.date.today() + datetime.timedelta(days=1)):  # experiment.date?
            to = experiment.subject.mail
            subject_reminder = "תזכורת לניסוי"
            body_reminder = f"""This is a reminder
            you have an experiment tomorrow at {subject.time}
            thanks"""  # fix time variable
            yag.send(to=to, subject=subject_reminder, contents=body_reminder)


# new experiment announcement
def exp_mail(email_list):
    subject_new = "ניסוי חדש!"
    body_new = ""
    yag.send(to=email_list, subject=subject_new, contents=body_new)


scheduler = BlockingScheduler()
job = scheduler.add_job(mail_reminders(), 'cron', hour=reminder_time)
scheduler.start()
