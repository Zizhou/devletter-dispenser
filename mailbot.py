import re, email, time, urllib, smtplib

from email.mime.multipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.mime.text import MIMEText
from email import Encoders

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'devletter.settings'

from django.conf import settings

import sys

def pack_donation(donation, send_to, game, url_get, url_return):
    mail = MIMEMultipart('alternative')
    mail['Subject'] = 'Thank you for "donating"'
    mail['From'] = settings.ROBOT_MAILER 
    mail['To'] = send_to
    message = donation + '.<br>' + 'Here is a code for ' + str(game) +'.<br>''To redeem it, go to '+url_get+'<br> If you would like to return it to us, go to '+url_return
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


