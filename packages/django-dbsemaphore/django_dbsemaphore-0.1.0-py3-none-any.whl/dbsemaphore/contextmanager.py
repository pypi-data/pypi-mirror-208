from contextlib import contextmanager
from threading import Thread, Event
from typing import List

from django.db import transaction

from .semaphore import acquire


@contextmanager
def semaphore_ticket(semaphore_name: str):
    """
    Obtains a semaphore ticket for the lifetime of this contextmanager, in a separate transaction (separate thread)
    """
    lock_request_outcome_determined = Event()
    request_release_event = Event()
    lock_acquired = [False]
    thelockthread = Thread(
        target=_semaphore_ticket,
        name=f'dbsemaphore-thread-{semaphore_name}',
        daemon=True,
        args=(
            semaphore_name,
            lock_acquired,
            lock_request_outcome_determined,
            request_release_event,
        ),
    )
    thelockthread.start()
    lock_request_outcome_determined.wait()
    try:
        yield lock_acquired[0]
    finally:
        request_release_event.set()
        thelockthread.join()


def _semaphore_ticket(semaphore_name: str, lock_acquired: List[bool], lock_request_outcome_determined: Event, request_release_event: Event):
    with transaction.atomic():
        ticket = acquire(semaphore_name)
        lock_acquired[0] = ticket
        lock_request_outcome_determined.set()
        if ticket is not None:
            request_release_event.wait()
