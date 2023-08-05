from django.db import models


class Ticket(models.Model):
    semaphore_name = models.CharField(null=False, blank=False, max_length=255, help_text="The name of the semaphore. Create as many rows as you want with the same name; the semaphore by that name will hold that many tickets.")

    def __str__(self):
        return f'Ticket {self.semaphore_name}@{self.id}'
