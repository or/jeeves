from django.db.models.signals import post_save
from django.dispatch import receiver

from jeeves.core.models import Build
from jeeves.core.routers import send_build_change
from jeeves.core.service import schedule_build
from jeeves.core.signals import (build_started, build_finished,
                                 job_started, job_finished)
from jeeves.github.service import report_status_for_job
from jeeves.notification.service import notify


@receiver(post_save, sender=Build)
def handle_build_saved(sender, instance, *args, **kwargs):
    build = instance
    send_build_change(build)

    if build.status in (Build.Status.CANCELLED, Build.Status.FINISHED):
        blocked_builds = Build.objects.filter(
            blocked_by=build,
            status=Build.Status.BLOCKED,
        ).order_by('build_id')

        for blocked_build in blocked_builds:
            schedule_build(blocked_build)


@receiver(build_started, sender='core')
def handle_build_started(sender, build, *args, **kwargs):
    notify(build, message="build #{} started".format(build.build_id))


@receiver(build_finished, sender='core')
def handle_build_finished(sender, build, *args, **kwargs):
    notify(build, message="build #{} finished".format(build.build_id))


@receiver(job_started, sender='core')
def handle_job_started(sender, job, *args, **kwargs):
    notify(job.build, message="job '{}' started".format(job.name))


@receiver(job_finished, sender='core')
def handle_job_finished(sender, job, *args, **kwargs):
    notify(job.build, message="job '{}' finished".format(job.name))
    report_status_for_job(job)
