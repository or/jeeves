from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from jeeves.core.models import Build, Job, UserProfile
from jeeves.core.routers import send_build_change, send_job_change
from jeeves.core.service import schedule_build


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


@receiver(post_save, sender=Job)
def handle_job_saved(sender, instance, *args, **kwargs):
    job = instance
    send_job_change(job)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
