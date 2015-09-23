from django.dispatch import receiver

from jeeves.core.signals import (build_started, build_finished,
                                 job_started, job_finished)
from jeeves.notification.service import Event, notify


@receiver(build_started, sender='core')
def handle_build_started(sender, build, *args, **kwargs):
    notify(Event.BUILD_STARTED, build=build)


@receiver(build_finished, sender='core')
def handle_build_finished(sender, build, *args, **kwargs):
    notify(Event.BUILD_FINISHED, build=build)


@receiver(job_started, sender='core')
def handle_job_started(sender, job, *args, **kwargs):
    notify(Event.JOB_STARTED, job=job)


@receiver(job_finished, sender='core')
def handle_job_finished(sender, job, *args, **kwargs):
    notify(Event.JOB_FINISHED, job=job)
