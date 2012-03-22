from django.contrib import admin
from models import Timely

class TimelyAdminMixin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (
                    ('start', 'end', 'day'),
                    ('recurrence', 'period', 'repeats'))
                }),
    )
