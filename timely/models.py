from datetime import datetime

from django.db import models

from django.utils.translation import ugettext, ugettext_lazy as _

now = lambda: datetime.now()

class TimelyManager(models.Manager):

    def later(self, start=None):
        if start is None:
            start = now()
        return self.filter(start__gte=start).order_by('-start')

recurrence = (('yr', _("Yearly")),
              ('mo', _("Monthly")),
              ('we', _("Weekly")),
              ('da', _("Daily")) )

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

    recurrence = models.CharField(_("recurs"),
                                  max_length=2,
                                  choices=recurrence,
                                  null=True)

    period = models.IntegerField(_("repeat every"),
                                 null=True)

    repeats = models.IntegerField(_("number of times"),
                                  null=True,
                                  help_text=_("Blank means until manually "
                                              "cancelled"))

    def save(self):
        if self.end is None:
            self.day = True
            self.start = datetime(self.start.year,
                                  self.start.month,
                                  self.start.day,
                                  0, 1, 0)
        return super(Timely, self).save()
