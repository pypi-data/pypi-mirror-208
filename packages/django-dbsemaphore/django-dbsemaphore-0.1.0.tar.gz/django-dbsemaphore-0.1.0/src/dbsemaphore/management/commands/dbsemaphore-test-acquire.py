from time import sleep
from sys import stderr

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from dbsemaphore.semaphore import acquire


class Command(BaseCommand):
    help = """Test a semaphore"""

    def add_arguments(self, parser):
        parser.add_argument('-n', '--dbname', help="Database name (useful for tests)")
        parser.add_argument('name', nargs=1, help="Name of semaphore")
        parser.add_argument('release', nargs='?', type=float, help="Release after X seconds")

    def handle(self, *args, **options):
        try:
            if options['dbname']:
                settings.DATABASES['default']['NAME'] = options['dbname']
            with transaction.atomic():
                ticket = acquire(options['name'][0])
                if ticket:
                    print(ticket.pk)
                else:
                    print(0)
                if options['release'] is not None:
                    sleep(options['release'])
                else:
                    print("Gently press Enter to release and exit…", file=stderr, end='')
                    input()
        except KeyboardInterrupt:
            exit("Interrupted")
