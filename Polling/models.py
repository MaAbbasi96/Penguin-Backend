from django.contrib.postgres.fields import JSONField
from django.db import models

from Polling.enums import PollStatus


class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)


class Poll(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=2048, null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=((st.value, st) for st in PollStatus),
                                              default=PollStatus.IN_PROGRESS.value)


class PollOption(models.Model):
    poll = models.ForeignKey(Poll)
    value = models.CharField(max_length=255)
    final = models.BooleanField(default=False)


class UserPoll(models.Model):
    user = models.ForeignKey(User)
    poll = models.ForeignKey(Poll)
    choices = JSONField()
