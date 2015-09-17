import jsonfield

from django.db import models

from jeeves.core.models import Build, Project


class NotificationTarget(models.Model):
    class Type:
        FLOWDOCK = "flowdock"

    TYPE_CHOICES = [
        (Type.FLOWDOCK, Type.FLOWDOCK),
    ]

    project = models.ForeignKey(Project)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    token = models.CharField(max_length=128)
    channel = models.CharField(max_length=256)


class NotificationMetadata(models.Model):
    build = models.ForeignKey(Build)
    type = models.CharField(max_length=10,
                            choices=NotificationTarget.TYPE_CHOICES)
    data = jsonfield.JSONField()

    class Meta:
        unique_together = ('build', 'type')
