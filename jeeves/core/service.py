import shlex
import subprocess
from datetime import datetime

from django.conf import settings

from jeeves.core.models import Build, Project


def get_log_file(instance, build_id):
    return settings.LOG_FILE_TEMPLATE.format(
        instance=instance, build_id=build_id)


def start_build(project, instance, branch=None, github_payload=None):
    branch = branch or instance
    build = Build.objects.create(project=project, instance=instance,
                                 branch=branch)
    build.log_file = get_log_file(instance, build.id)

    build.start_time = datetime.now()
    build.status = Build.Status.RUNNING
    build.save()

    command_context = dict(
        instance=instance,
        branch=branch,
        github=github_payload,
        build_id=build.id,
    )
    command = settings.BUILD_COMMAND.format(**command_context)
    print(command)
    try:
        result = subprocess.check_call(shlex.split(command))
    except subprocess.CalledProcessError as e:
        result = e.returncode

    if not result:
        build.result = Build.Result.SUCCESS
    else:
        build.result = Build.Result.FAILURE

    build.status = Build.Status.FINISHED
    build.end_time = datetime.now()
    build.save()


def handle_push_hook_request(payload):
    branch = payload['ref'][len('refs/heads/'):]
    project = Project.objects.get_for_github_event(payload)
    if not project:
        return

    start_build(project, branch, github_payload=payload)
