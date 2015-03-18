##schedule this script with a cron or something
from django.core.management.base import BaseCommand, CommandError

import datetime, mailbot

from dispenser.models import Code, Settings

class Command(BaseCommand):

    help = 'runs through any codes with a uuid assigned and checks for expiration'

    def handle(self, *args, **options):
        my_settings = Settings.objects.all()[0]

        queryset = Code.objects.filter(uuid_assigned = True).exclude(uuid_claimed = True)
        print datetime.datetime.utcnow()
        for code in queryset:
            if code.uuid_expired.replace(tzinfo = None) > datetime.datetime.utcnow() and code.uuid_expired.replace(tzinfo = None)- datetime.timedelta(1) < datetime.datetime.utcnow():
                print 'warning issued for ' + str(code)
                message = 'Your code for ' + str(code.game.game) + ' is expiring in one day.<br> Go to ' + my_settings.global_url + '?code='+code.uuid +' to redeem it.'
                mailbot.send_mail(mailbot.pack_MIME(message, code.assigned, 'Your code is expiring'), code.assigned)

            if code.uuid_expired.replace(tzinfo = None) < datetime.datetime.utcnow():
                print 'resetting ' + str(code)
                code.uuid_reset()
                code.game.update_count()

            print '~~~~~'
