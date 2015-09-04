from django.db.models.signals import post_save
from django.dispatch import receiver

from jeeves.core.models import Build
from jeeves.core.routers import send_build_change


@receiver(post_save, sender=Build)
def handle_build_saved(sender, instance, *args, **kwargs):
    send_build_change(instance)
