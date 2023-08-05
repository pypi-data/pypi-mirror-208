from django.contrib import admin

from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_filter = ('semaphore_name',)
    list_display = ('__str__', 'semaphore_name',)
    ordering = ('semaphore_name', 'pk')
