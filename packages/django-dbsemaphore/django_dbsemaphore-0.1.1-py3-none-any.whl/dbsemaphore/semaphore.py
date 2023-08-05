from typing import Union

from django.db import transaction, connection

from .models import Ticket
from . import NotInTransactionException


def acquire(semaphore_name: str) -> Union[Ticket, None]:
    """
    Acquire a ticket for a semaphore. Returns the ticket if successful, and None if there are none available.
    It is the callers responsibility to be inside a transaction context.
    """
    if not transaction.get_connection().in_atomic_block:
        raise NotInTransactionException('Semaphore tickets must be acquired inside a DB transaction block')
    return Ticket.objects.order_by('pk').select_for_update(skip_locked=True).filter(semaphore_name=semaphore_name).first()


@transaction.atomic
def make(semaphore_name: str, amt_tickets: int = 1):
    """
    Creates a new semaphore or adjusts the number of tickets of an existing one.
    Locks the table so that only one such adjustment can be done at a time.
    A downwards adjustment involves deletion of ticket rows, this blocks on rows
    representing currently issued tickets. Thus, the downward adjustment will take place
    once enough tickets have been returned to the semaphore.
    """
    connection.cursor().execute(f"LOCK TABLE {connection.ops.quote_name(Ticket._meta.db_table)} IN SHARE ROW EXCLUSIVE MODE")
    extants = Ticket.objects.filter(semaphore_name=semaphore_name).values_list('pk', flat=True)
    if len(extants) == amt_tickets:
        return  # Just right, nothing to do
    elif len(extants) < amt_tickets:
        Ticket.objects.bulk_create((Ticket(semaphore_name=semaphore_name) for i in range(amt_tickets - len(extants))))
    else:
        Ticket.objects.filter(pk__in=extants[amt_tickets:]).delete()


def destroy(semaphore_name: str):
    """
    Removes a semaphore.
    """
    make(semaphore_name, 0)


def list():
    """
    Returns a list of available semaphores and the number of tickets they each hold.
    """
    with connection.cursor() as cur:
        cur.execute(f"""
            SELECT
                semaphore_name,
                count(id)
            FROM
                {connection.ops.quote_name(Ticket._meta.db_table)}
            GROUP BY
                semaphore_name;
        """)
        return dict(cur)
