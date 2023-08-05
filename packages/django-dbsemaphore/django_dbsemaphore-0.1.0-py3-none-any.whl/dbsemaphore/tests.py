from subprocess import Popen, PIPE, DEVNULL
from sys import executable as this_python

from django.test.testcases import TransactionTestCase
from django.conf import settings

from .semaphore import make, list

TEST_SEMAPHORE = "Test"


class SemaphoreTest(TransactionTestCase):
    @classmethod
    def setUp(cls):
        # Create a semaphore with 2 tickets
        make(TEST_SEMAPHORE, 2)

    def test_list(self):
        self.assertEqual(list(), {TEST_SEMAPHORE: 2})

    def test_enlarge(self):
        make(TEST_SEMAPHORE, 3)
        self.assertEqual(list(), {TEST_SEMAPHORE: 3})

    def test_shrink(self):
        make(TEST_SEMAPHORE, 2)
        self.assertEqual(list(), {TEST_SEMAPHORE: 2})

    def test_acquire(self):
        """
        Launch three independent processes, each of which
        will attempt to acquire a ticket from the semaphore.
        We expect two to succeed and one to fail.
        """
        call_argv = [this_python, 'manage.py', 'dbsemaphore-test-acquire', '--dbname', settings.DATABASES['default']['NAME'], TEST_SEMAPHORE]
        launched = [Popen(call_argv, stdin=PIPE, stdout=PIPE, stderr=DEVNULL, text=True) for i in range(3)]
        outcomes = {int(p.stdout.read(1)) for p in launched}
        for p in launched:
            p.communicate(input="\n")
        self.assertEqual(outcomes, {0, 1, 2})
