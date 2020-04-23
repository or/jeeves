from django.db import models

from jeeves.core.models import Build, Project
from jeeves.util import JsonFieldTransitionHelper


class NotificationTarget(models.Model):
    class Type:
        FLOWDOCK = "flowdock"

    TYPE_CHOICES = [
        (Type.FLOWDOCK, Type.FLOWDOCK),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    token = models.CharField(max_length=128)
    channel = models.CharField(max_length=256)
    enabled = models.BooleanField(default=True)


class NotificationMetadata(models.Model):
    build = models.OneToOneField(Build, primary_key=True, on_delete=models.CASCADE)
    data = JsonFieldTransitionHelper(default=dict)
