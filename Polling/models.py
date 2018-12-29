from jdatetime import date as jdate

from django.contrib.postgres.fields import JSONField
from django.db import models

from Polling.enums import PollStatus


class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class Poll(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=2048, null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=((st.value, st) for st in PollStatus),
                                              default=PollStatus.IN_PROGRESS.value)

    def __str__(self):
        return self.title


class AbstractPollOption(models.Model):
    poll = models.ForeignKey(Poll)
    final = models.BooleanField(default=False)

    class Meta:
        abstract = True


class NormalPollOption(AbstractPollOption):
    value = models.CharField(max_length=255)


class WeeklyPollOption(AbstractPollOption):
    DAYS_OF_WEEK = [
        (5, jdate.j_weekdays_fa[0]),
        (6, jdate.j_weekdays_fa[1]),
        (0, jdate.j_weekdays_fa[2]),
        (1, jdate.j_weekdays_fa[3]),
        (2, jdate.j_weekdays_fa[4]),
        (3, jdate.j_weekdays_fa[5]),
        (4, jdate.j_weekdays_fa[6]),
    ]

    weekday = models.PositiveSmallIntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()


class UserPoll(models.Model):
    user = models.ForeignKey(User)
    poll = models.ForeignKey(Poll)
    choices = JSONField()
