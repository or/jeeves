from datetime import datetime

from django.conf import settings

from jeeves.core.models import Build


def get_log_file(instance, build_id):
    return settings.LOG_FILE_TEMPLATE.format(
        instance=instance, build_id=build_id)


def start_build(instance, branch=None):
    branch = branch or instance
    build = Build.objects.create(instance=instance, branch=branch)
    build.log_file = get_log_file(instance, build.id)

    build.start_time = datetime.now()
    build.status = Build.Status.RUNNING
    build.save()

    # run things

    build.end_time = datetime.now()
    build.save()
