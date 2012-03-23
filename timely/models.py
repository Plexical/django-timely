from datetime import datetime, timedelta

from django.db import models

from django.utils.translation import ugettext, ugettext_lazy as _

now = lambda: datetime.now()

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

    def period(self, start, end):
        if start == 'now':
            start = now()
        return self.filter(start__gte=start).order_by('-start')

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
