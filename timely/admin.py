from django.contrib import admin

from django.utils.translation import ugettext, ugettext_lazy as _

class TimelyAdminMixin(admin.ModelAdmin):
    fieldsets = (
        (_("When"),
         {'fields': (('start', 'end', 'day'),) }),
    )
