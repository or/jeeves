import time

from django.core.management.base import BaseCommand

from jeeves.core.models import Project, Build
from jeeves.core.service import schedule_new_build


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('project')

    def handle(self, *args, **options):
        project = Project.objects.get(name=options['project'])
        while True:
            build_ids = list(sorted(Build.objects.values_list('build_id', flat=True), reverse=True))
            if len(build_ids) > 100:
                Build.objects.filter(build_id__lt=build_ids[100]).delete()
            schedule_new_build(project, reason='Triggered from management command')
            time.sleep(12)
