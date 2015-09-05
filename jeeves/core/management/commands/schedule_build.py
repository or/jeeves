from django.core.management.base import BaseCommand

from jeeves.core.models import Project
from jeeves.core.service import schedule_new_build


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('project')

    def handle(self, *args, **options):
        project = Project.objects.get(name=options['project'])
        schedule_new_build(project, reason='Triggered from management command')
