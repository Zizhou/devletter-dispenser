##schedule this script with a cron or something
from django.core.management.base import BaseCommand, CommandError

from dispenser.models import Code, Settings

class Command(BaseCommand):

    help = 'does...nothing?'
    def handle(self, *args, **options):

        print 'oh god what am i doing'
