import os

import jsonfield

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone


def get_total_number_of_seconds(delta):
    return 86400 * delta.days + delta.seconds + delta.microseconds / 1000000.0


def get_elapsed_time_in_seconds(from_time, to_time):
    elapsed_time = to_time - from_time
    return get_total_number_of_seconds(elapsed_time)


def get_elapsed_time(from_time, to_time):
    float_num_secs = get_elapsed_time_in_seconds(from_time, to_time)
    if float_num_secs < 1:
        if float_num_secs < 0.1:
            return '0.1 secs'

        return '{:.1f} secs'.format(float_num_secs)

    num_secs = int(float_num_secs)
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


class UserProfile(models.Model):
    user = models.OneToOneField(User)

    github_account = models.CharField(max_length=128, null=True, blank=True)
    flowdock_account = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return "{}'s profile".format(self.user)


class Project(models.Model):
    name = models.CharField(
        max_length=64, help_text="the name of the project")
    slug = models.SlugField(help_text="the slug to identify the project")
    description = models.CharField(
        max_length=1024, help_text="a description of the project")
    blocking_key_template = models.CharField(
        max_length=2048, help_text="a template for a blocking key, "
        "builds with the same key will block each other; a constant key "
        "will result in a blocking build queue",
        null=True, blank=True)

    def __str__(self):
        return self.name

    def get_num_running_builds(self):
        return self.build_set.filter(status=Build.Status.RUNNING).count()


class JobDescription(models.Model):
    project = models.ForeignKey(Project)
    name = models.SlugField(
        name="name",
        max_length=128, help_text="the name of the job inside the build")
    dependencies = models.CharField(
        max_length=1024, null=True, blank=True,
        help_text="a list of job names this job depends on")
    script = models.TextField(help_text="the script to run for the job")
    report_result = models.BooleanField(
        help_text="flag whether the result of this job should be "
                  "reported on GitHub")

    class Meta:
        unique_together = ('project', 'name')

    def __str__(self):
        return self.project.slug + '.' + self.name


class Build(models.Model):
    class Result:
        SUCCESS = "success"
        FAILURE = "failure"
        ERROR = "error"

    class Status:
        SCHEDULED = "scheduled"
        BLOCKED = "blocked"
        RUNNING = "running"
        FINISHED = "finished"
        CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (Status.SCHEDULED, Status.SCHEDULED),
        (Status.BLOCKED, Status.BLOCKED),
        (Status.RUNNING, Status.RUNNING),
        (Status.FINISHED, Status.FINISHED),
        (Status.CANCELLED, Status.CANCELLED),
    ]

    RESULT_CHOICES = [
        (Result.SUCCESS, Result.SUCCESS),
        (Result.FAILURE, Result.FAILURE),
        (Result.ERROR, Result.ERROR),
    ]

    project = models.ForeignKey(Project)
    build_id = models.IntegerField(null=True, blank=True)
    blocking_key = models.CharField(max_length=1024, null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES,
                              default=Status.SCHEDULED, db_index=True)
    creation_time = models.DateTimeField(auto_now_add=True, db_index=True)
    start_time = models.DateTimeField(null=True, blank=True, db_index=True)
    end_time = models.DateTimeField(null=True, blank=True)
    modified_time = models.DateTimeField(auto_now=True, db_index=True)
    repository = models.CharField(max_length=512, null=True, blank=True)
    branch = models.CharField(max_length=1024, null=True, blank=True)
    commit = models.CharField(max_length=40, null=True, blank=True)
    metadata = jsonfield.JSONField()
    reason = models.CharField(max_length=128, null=True, blank=False)
    blocked_by = models.ForeignKey('Build', null=True, blank=True)
    result = models.CharField(max_length=16, choices=RESULT_CHOICES,
                              null=True, blank=True)
    result_details = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('project', 'build_id')
        index_together = [
            ('project', 'build_id'),
            ('project', 'blocking_key', 'build_id'),
        ]

    def __str__(self):
        return '#{}'.format(self.build_id)

    def save(self, *args, **kwargs):
        if not self.id and not self.build_id:
            last_id = \
                Build.objects.filter(project=self.project) \
                .aggregate(last_id=models.Max('build_id'))['last_id']
            self.build_id = last_id + 1 if last_id else 1

        super(Build, self).save(*args, **kwargs)

    def get_age_in_seconds(self):
        return get_total_number_of_seconds(timezone.now() - self.creation_time)

    def get_age(self):
        num_seconds = self.get_age_in_seconds()

        units = [
            ('year', 60 * 60 * 24 * 365.2425),
            ('month', 60 * 60 * 24 * 30.5),
            ('week', 60 * 60 * 24 * 7),
            ('day', 60 * 60 * 24),
            ('hour', 60 * 60),
            ('min', 60),
            ('sec', 1),
        ]
        for unit, length in units:
            number = num_seconds // length
            if number or length == 1:
                return '{} {}{}'.format(
                    number, unit, 's' if number != 1 else '')

    def get_duration_in_seconds(self):
        if not self.start_time or not self.end_time:
            return None

        return get_elapsed_time_in_seconds(self.start_time, self.end_time)

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

        return 'https://github.com/{}/'.format(self.repository)

    def get_commit_link(self):
        if not self.repository or not self.commit:
            return None

        return 'https://github.com/{}/commit/{}' \
            .format(self.repository, self.commit)

    def get_branch_link(self):
        if not self.repository or not self.branch:
            return None

        return 'https://github.com/{}/tree/{}' \
            .format(self.repository, self.branch)

    def get_commit(self):
        if not self.metadata:
            return None

        return self.metadata.get('head_commit')

    def is_cancellable(self):
        return self.status in (Build.Status.SCHEDULED, Build.Status.BLOCKED)

    def get_log(self):
        data = []
        for job in self.job_set.order_by('id'):
            data.append("# Running job '{}'".format(job.name))
            data.append(job.get_log().rstrip('\n '))
            if job.status == Job.Status.FINISHED:
                data.append(
                    "# Job '{}' finished with {}\n"
                    .format(
                        job.name,
                        'success' if
                        job.result == Job.Result.SUCCESS else 'failure'))

        return '\n'.join(data)

    def get_script_context(self):
        context = dict(
            branch=self.branch,
            commit=self.commit,
            metadata=self.metadata,
            build_id=self.id,
            build_url=self.get_external_url(),
            build_status=self.status,
            build_result=self.result,
            build_result_details=self.result_details,
        )

        if hasattr(self, 'notificationmetadata'):
            context['notification'] = self.notificationmetadata.data

        return context

    def get_jobs(self):
        return self.job_set.order_by('id')


class BuildSource(models.Model):
    build = models.OneToOneField(Build, primary_key=True, related_name="source")
    source = models.ForeignKey(Build, related_name="copies")
    user = models.ForeignKey(User)


class Job(models.Model):
    class Status:
        RUNNING = "running"
        FINISHED = "finished"

    class Result:
        SUCCESS = "success"
        FAILURE = "failure"
        ERROR = "failure"

    STATUS_CHOICES = [
        (Status.RUNNING, Status.RUNNING),
        (Status.FINISHED, Status.FINISHED),
    ]

    RESULT_CHOICES = [
        (Result.SUCCESS, Result.SUCCESS),
        (Result.FAILURE, Result.FAILURE),
        (Result.ERROR, Result.ERROR),
    ]

    build = models.ForeignKey(Build)
    name = models.SlugField(name="name", max_length=128)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES,
                              default=Status.RUNNING, db_index=True)
    start_time = models.DateTimeField(auto_now_add=True, db_index=True)
    end_time = models.DateTimeField(null=True, blank=True)
    modified_time = models.DateTimeField(auto_now=True, db_index=True)
    result = models.CharField(max_length=16, choices=RESULT_CHOICES,
                              null=True, blank=True)
    result_details = models.TextField(null=True, blank=True)
    log_file = models.FileField(
        storage=FileSystemStorage(location="logs"), null=True, blank=True)

    class Meta:
        unique_together = ('build', 'name')

    def __str__(self):
        return '{}.{}'.format(self.build, self.name)

    def get_log(self, offset=0):
        if not self.log_file:
            return None

        self.log_file.open()
        self.log_file.seek(offset)
        data = self.log_file.read().decode('utf-8')
        self.log_file.close()

        return data, os.path.getsize(self.log_file.path)

    def get_duration_in_seconds(self):
        if not self.start_time or not self.end_time:
            return None

        return get_elapsed_time_in_seconds(self.start_time, self.end_time)

    def get_duration(self):
        if not self.start_time or not self.end_time:
            return None

        return get_elapsed_time(self.start_time, self.end_time)

    def get_elapsed_time(self):
        if self.status == Job.Status.FINISHED:
            return None

        if not self.start_time:
            return None

        return get_total_number_of_seconds(timezone.now() - self.start_time)

    def get_estimated_time(self):
        last_job = \
            Job.objects.filter(
                name=self.name,
                status=Job.Status.FINISHED,
                result=Job.Result.SUCCESS,
                start_time__isnull=False,
                end_time__isnull=False,
                build__build_id__lt=self.build.build_id
            ).order_by('-build__build_id').first()

        if not last_job:
            return None

        return get_total_number_of_seconds(
            last_job.end_time - last_job.start_time)
