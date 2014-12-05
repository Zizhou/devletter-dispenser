import re, email, time, urllib, smtplib

from email.mime.multipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.mime.text import MIMEText
from email import Encoders

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'devletter.settings'

from django.conf import settings

import sys

def pack_MIME(message, send_to, subject):
    mail = MIMEMultipart('alternative')
    mail['Subject'] = subject 
    mail['From'] = settings.ROBOT_MAILER 
    mail['To'] = send_to
    body = MIMEText(message, 'html', 'UTF-8')
    mail.attach(body)

    return mail

def send_mail(mail, address):
    print >>sys.stderr, mail
    #probably should be a setting and not hardcoded, but eh
    server = smtplib.SMTP('smtp.gmail.com','587')
    server.ehlo()
    server.starttls() 
    server.login(settings.ROBOT_MAILER, settings.ROBOT_PASSWORD)
    server.sendmail(settings.ROBOT_MAILER, address, mail.as_string())
    server.quit()


