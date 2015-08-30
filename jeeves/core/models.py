from datetime import timedelta
from math import exp

from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone


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

    def get_duration(self):
        if not self.start_time or not self.end_time:
            return None

        elapsed_time = self.end_time - self.start_time
        num_secs = elapsed_time.days * 86400 + elapsed_time.seconds
        mins = int(num_secs / 60)
        secs = int(num_secs - mins * 60)
        chunks = []
        if mins > 0:
            chunks.append('{} mins'.format(mins))
        if secs > 0:
            chunks.append('{} secs'.format(secs))

        total = ', '.join(chunks)
        if not total:
            total = '0 secs'

        return total

    def get_progress(self):
        if self.status == Build.Status.FINISHED:
            return {'percentage': 100}

        last_build = \
            Build.objects.filter(
                project=self.project,
                status=Build.Status.FINISHED,
                result=Build.Result.SUCCESS,
                start_time__isnull=False,
                end_time__isnull=False,
                build_id__lt=self.build_id
            ).order_by('-build_id').first()

        diff = timezone.now() - self.start_time
        if not last_build:
            return {
                'percentage':
                100.0 * (1.0 - exp(-diff / timedelta(seconds=300))),
            }

        previous_duration = last_build.end_time - last_build.start_time

        if diff > previous_duration:
            over = diff - previous_duration
            return {
                'percentage': 100.0 * previous_duration / (1.1 * diff),
                'over': 100.0 * over / (1.1 * diff),
            }

        return {'percentage': 100.0 * diff / previous_duration}
