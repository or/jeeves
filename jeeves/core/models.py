import json
from math import exp

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone


def get_total_number_of_seconds(delta):
    return 86400 * delta.days + delta.seconds


def get_elapsed_time(from_time, to_time):
    elapsed_time = to_time - from_time
    num_secs = get_total_number_of_seconds(elapsed_time)
    mins = int(num_secs / 60)
    secs = int(num_secs - mins * 60)
    chunks = []
    if mins > 0:
        chunks.append('{} min{}'.format(mins, 's' if mins != 1 else ''))
    if secs > 0:
        chunks.append('{} sec{}'.format(secs, 's' if secs != 1 else ''))

    total = ', '.join(chunks)
    if not total:
        total = '0 secs'

    return total


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
        SCHEDULED = "scheduled"
        RUNNING = "running"
        FINISHED = "finished"

    class Result:
        SUCCESS = "success"
        FAILURE = "failure"

    STATUS_CHOICES = [
        (Status.SCHEDULED, Status.SCHEDULED),
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
                              default=Status.SCHEDULED)
    creation_time = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    modified_time = models.DateTimeField(auto_now=True, db_index=True)
    repository = models.CharField(max_length=512, null=True, blank=True)
    branch = models.CharField(max_length=1024, null=True, blank=True)
    metadata = models.TextField(null=True, blank=True)
    log_file = models.FileField(
        storage=FileSystemStorage(location="logs"), null=True, blank=True)
    result = models.CharField(max_length=16, choices=RESULT_CHOICES,
                              null=True, blank=True)
    reason = models.CharField(max_length=128, null=True, blank=False)

    class Meta:
        unique_together = ('project', 'build_id')

    def get_log(self):
        if not self.log_file:
            return ''

        self.log_file.open()
        self.log_file.seek(0)
        data = self.log_file.read()
        self.log_file.close()

        return data

    def save(self, *args, **kwargs):
        if not self.id and not self.build_id:
            self.build_id = \
                Build.objects.filter(project=self.project) \
                .aggregate(last_id=models.Max('build_id'))['last_id'] + 1

        super(Build, self).save(*args, **kwargs)

    def get_duration(self):
        if not self.start_time or not self.end_time:
            return None

        return get_elapsed_time(self.start_time, self.end_time)

    def get_elapsed_time(self):
        if self.status == Build.Status.FINISHED:
            return None

        if not self.start_time:
            return None

        return get_total_number_of_seconds(timezone.now() - self.start_time)

    def get_estimated_time(self):
        last_build = \
            Build.objects.filter(
                project=self.project,
                status=Build.Status.FINISHED,
                result=Build.Result.SUCCESS,
                start_time__isnull=False,
                end_time__isnull=False,
                build_id__lt=self.build_id
            ).order_by('-build_id').first()

        if not last_build:
            return None

        previous_duration = get_total_number_of_seconds(
            last_build.end_time - last_build.start_time)

        return previous_duration

    def get_external_url(self):
        return settings.BASE_URL + \
            reverse(
                'build-view',
                kwargs=dict(project_slug=self.project.slug,
                            build_id=self.build_id))

    def get_repository_link(self):
        if not self.repository:
            return None

        return 'https://github.com/{}'.format(self.repository)

    def set_metadata(self, metadata):
        self.metadata = json.dumps(metadata)

    def get_metadata(self):
        return json.loads(self.metadata)
