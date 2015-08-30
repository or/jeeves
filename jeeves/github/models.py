from django.db import models

from jeeves.core.models import Project


class GithubRepository(models.Model):
    name = models.CharField(max_length=512,
                            help_text="the name of the GitHub repository "
                                      "in <account>/<repository> form",
                            unique=True)

    def __str__(self):
        return self.name


class GithubWebhookMatch(models.Model):
    repository = models.ForeignKey(
        GithubRepository,
        help_text="the repository on GitHub")

    branch_match = models.CharField(
        max_length=512,
        help_text="a wildcard pattern of the branches to match")

    project = models.ForeignKey(
        Project, help_text="the Jeeves project")

    exclude = models.BooleanField()

    class Meta:
        unique_together = ('project', 'repository', 'branch_match')

    def __str__(self):
        return "{}{}:{}@{}".format(
            '!' if self.exclude else '',
            self.project.slug,
            self.repository,
            self.branch_match)
