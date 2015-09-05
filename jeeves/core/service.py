import os
import stat
import subprocess
import tempfile
from io import StringIO

from celery import shared_task

from django.core.files import File
from django.utils import timezone

from .models import Build
from .signals import build_start, build_finished


def schedule_build(build):
    build.status = Build.Status.SCHEDULED
    build.save()

    start_build.delay(build.id)


def schedule_new_build(project, repository=None, branch=None,
                       metadata=None, reason=None, commit=None):
    build = Build.objects.create(project=project, repository=repository,
                                 branch=branch, reason=reason, commit=commit)
    build.set_metadata(metadata)
    schedule_build(build)

    return build


def copy_and_schedule_new_build(build, user=None):
    reason = "re-build #{}".format(build.build_id)
    if user:
        reason += ' by {}'.format(user.username)

    new_build = schedule_new_build(
        build.project, repository=build.repository, branch=build.branch,
        metadata=build.get_metadata(), reason=reason, commit=build.commit)

    return new_build


@shared_task
def start_build(build_pk):
    build = Build.objects.get(pk=build_pk)
    if build.status != Build.Status.SCHEDULED:
        # if this build is not scheduled anymore, then ignore this task
        return

    script_context = dict(
        branch=build.branch,
        commit=build.commit,
        metadata=build.get_metadata(),
        build_id=build.id,
        build_url=build.get_external_url()
    )

    if build.project.blocking_key_template:
        build.blocking_key = \
            build.project.blocking_key_template.format(**script_context)
        blocking_build = Build.objects.filter(
            project=build.project,
            blocking_key=build.blocking_key,
            build_id__lt=build.build_id
        ).exclude(
            status=Build.Status.FINISHED
        ).order_by('-build_id').first()

        build.blocked_by = blocking_build
    else:
        # explicitly set this, because the project's blocking_key_template
        # may have changed since a build was blocked
        build.blocking_key = None
        build.blocked_by = None

    if build.blocked_by:
        # we are still or are now blocked by a build, so only save
        # and bail out; the build will be rescheduled when the blocking
        # build has finished
        build.status = Build.Status.BLOCKED
        build.save()
        return

    build.log_file.save('build-{:05d}-{:05d}.log'.format(build.project.id,
                                                         build.build_id),
                        File(StringIO()))
    build.status = Build.Status.RUNNING
    build.start_time = timezone.now()
    build.save()

    (fd, file_path) = tempfile.mkstemp(suffix='.sh', prefix='tmp')
    script = build.project.script
    script = script.format(**script_context)
    os.write(fd, b"#!/bin/bash -e\n")
    os.write(fd, script.replace('\r', '\n').encode('utf-8'))
    os.close(fd)

    st = os.stat(file_path)
    os.chmod(file_path, st.st_mode | stat.S_IEXEC)

    build_start.send('core', build=build)

    env_removals = ['DJANGO_SETTINGS_MODULE', 'VIRTUAL_ENV', 'CD_VIRTUAL_ENV']
    env = dict(os.environ)
    for env_entry in env_removals:
        if env_entry in env:
            env.pop(env_entry)

    out = open(build.log_file.path, 'w')
    try:
        result = subprocess.check_call(
            [file_path],
            stdout=out,
            stderr=out,
            env=env)
    except subprocess.CalledProcessError as e:
        result = e.returncode

    if not result:
        build.result = Build.Result.SUCCESS
    else:
        build.result = Build.Result.FAILURE

    build.status = Build.Status.FINISHED
    build.end_time = timezone.now()
    build.save()

    build_finished.send('core', build=build)
