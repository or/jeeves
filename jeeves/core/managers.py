from django.db import models


class ProjectManager(models.Manager):
    def get_for_github_event(self, payload):
        return self.get_queryset()[0]
