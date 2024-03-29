from copy import deepcopy
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

    def period(self, after, end=None):
        if isinstance(after, basestring):
            after = apptime(after)
        if isinstance(end, basestring):
            end = apptime(end)
        if end is None:
            end = apptime('2200-01-01')
        return (self.filter(end__gte=after)
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

    unit = models.CharField(_("unit"),
                            max_length=7,
                            choices=units)

    def save(self, *args, **kw):
        # XXX will use generic.GenericForeignKey when I get time to
        # learn about them and get admin inlines to work with them

        creating = self.pk is None
        res = super(Repetition, self).save(*args, **kw)

        # XXX the following line is probably wrong on SO many levels...
        if creating and self.repeats.count() == 0:
            first = self.first
            self.repeats.add(first)
            for nth in range(1, self.repeat):
                repeated = deepcopy(first)
                repeated.pk = None
                repeated.start = future(first.start, nth, self.every, self.unit)
                repeated.end = future(first.end, nth, self.every, self.unit)
                repeated.save()
                self.repeats.add(repeated)

        return super(Repetition, self).save(*args, **kw)

    def refresh(self, changed):
        # XXX won't scale
        old = type(changed).objects.get(pk=changed.pk)
        delta_start = changed.start - old.start
        delta_end = changed.end - old.end
        for model in self.repeats.exclude(pk=changed.pk):
            model.start += delta_start
            model.end += delta_end
            model.save(cascade=False) # is this ok???

def nominalize(dt, minute=0):
    """
    Returns a new `datetime` object with a nominal time set on it
    suitable for full day events (i.e. we don't care about the time
    part of `datetime`).

    The `minute` parameter can be used to add an extra minute if the
    `datetime` is the end time.
    """
    return datetime(dt.year, dt.month, dt.day, 2, minute, 0)

class Timely(models.Model):

    objects = TimelyManager()

    class Meta:
        ordering = ['start']
        abstract = True

    start = models.DateTimeField(_("start"))
    end = models.DateTimeField(_("end"),
                               null=True,
                               help_text=_("The end time must be later than "
                                           "the start time."))
    day = models.BooleanField(_("whole day"), default=False)

    def save(self, *args, **kwargs):
        if self.end is None:
            self.day = True
            self.end = self.start

        if self.day:
            self.start = nominalize(self.start)
        if self.day and self.end:
            self.end = nominalize(self.end, 1)

        if kwargs.pop('cascade', True):
            try:
                self.repeats.get().refresh(self)
            except:
                # XXX failed to find the right DoesNotExist
                pass

        return super(Timely, self).save(*args, **kwargs)
