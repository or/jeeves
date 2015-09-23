from django.dispatch import receiver

from jeeves.core.signals import job_finished
from jeeves.github.service import report_status_for_job


@receiver(job_finished, sender='core')
def handle_job_finished(sender, job, *args, **kwargs):
    report_status_for_job(job)
