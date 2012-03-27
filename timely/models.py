from datetime import datetime, timedelta

import times

from django.db import models
from django.conf import settings

from django.utils.translation import ugettext, ugettext_lazy as _

def apptime(dt, tz=None):
    if dt == 'now':
        dt = times.now()
    if tz is None:
        tz = settings.TIME_ZONE
    return times.to_universal(dt, tz)

def future(pt, nth, every, unit):
    """
    Calculates the timedelta needed to add to `pt` for it to happen
    for the `nth` time `every` `unit`.
    """
    delta = nth * every
    if unit == 'years':
        # timedelta doesn't have years but that's no problem, years
        # are nice and linear.
        return datetime(pt.year + delta,
                        pt.month,
                        pt.day,
                        pt.hour,
                        pt.second)
    return pt + timedelta(**{unit: delta})

class TimelyManager(models.Manager):

    def period(self, start, end=None):
        if isinstance(start, basestring):
            start = apptime(start)
        if isinstance(end, basestring):
            end = apptime(end)
        if end is None:
            end = apptime('2200-01-01')
        return (self.filter(start__gte=start)
                .filter(start__lt=end)
                .order_by('start'))

"Stored strings maps directly to datetime.timedelta parameter names"
units = (('years', _("Year")),
         ('months', _("Month")),
         ('weeks', _("Week")),
         ('days', _("Day")) )

class Repetition(models.Model):

    class Meta:
        abstract = True

    repeat = models.IntegerField(_("repeat"),
                                 default=0,
                                 help_text=_('times'))

    every = models.IntegerField(_("every"),
                                null=True)

    unit = models.CharField("",
                            max_length=7,
                            choices=units)

class Timely(models.Model):

    objects = TimelyManager()

    class Meta:
        abstract = True

    start = models.DateTimeField(_("start"))
    end = models.DateTimeField(_("end"),
                               null=True,
                               help_text=_("The end time must be later than "
                                           "the start time."))
    day = models.BooleanField(_("whole day"), default=False)

    def save(self):
        if self.end is None:
            self.day = True
            self.end = self.start

        if self.day:
            self.start = datetime(self.start.year,
                                  self.start.month,
                                  self.start.day,
                                  0, 1, 0)
        if self.day and self.end:
            self.end = datetime(self.end.year,
                                self.end.month,
                                self.end.day,
                                23, 59, 59)

        return super(Timely, self).save()

    def repetition(self, nth):
        copy = deepcopy(self)
        copy.pk = None
        copy.start = future(self.start, nth, self.every, self.unit)
        copy.end = future(self.end, nth, self.every, self.unit)
        return copy
