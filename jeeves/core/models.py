from django.core.files.storage import FileSystemStorage
from django.db import models


fs = FileSystemStorage(location='/media/photos')


class Project(models.Model):
    name = models.CharField(
        max_length=64, help_text="the name of the project")
    slug = models.SlugField(help_text="the slug to identify the project")
    description = models.CharField(
        max_length=1024, help_text="a description of the project")
    script = models.TextField(help_text="the script to run for the build")

    def __str__(self):
        return self.name

    def get_num_running_builds(self):
        return self.build_set.filter(status=Build.Status.RUNNING).count()


class Build(models.Model):
    class Status:
        CREATED = "created"
        RUNNING = "running"
        FINISHED = "finished"

    class Result:
        SUCCESS = "success"
        FAILURE = "failure"

    STATUS_CHOICES = [
        (Status.CREATED, Status.CREATED),
        (Status.RUNNING, Status.RUNNING),
        (Status.FINISHED, Status.FINISHED),
    ]
    RESULT_CHOICES = [
        (Result.SUCCESS, Result.SUCCESS),
        (Result.FAILURE, Result.FAILURE),
    ]

    project = models.ForeignKey(Project)
    build_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES,
                              default=Status.CREATED)
    instance = models.CharField(max_length=1024)
    branch = models.CharField(max_length=1024, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    log_file = models.FileField(
        storage=FileSystemStorage(location="logs"), null=True, blank=True)
    result = models.CharField(max_length=16, choices=RESULT_CHOICES,
                              null=True, blank=True)

    class Meta:
        unique_together = ('project', 'build_id')

    def get_log(self):
        return self.log_file.read()

    def save(self, *args, **kwargs):
        if not self.id and not self.build_id:
            self.build_id = \
                Build.objects.filter(project=self.project).count() + 1

        super(Build, self).save(*args, **kwargs)
