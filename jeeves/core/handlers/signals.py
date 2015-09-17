from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from jeeves.core.models import Build
from jeeves.core.routers import send_build_change, send_build_delete
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


@receiver(post_delete, sender=Build)
def handle_build_delete(sender, instance, *args, **kwargs):
    send_build_delete(instance)
