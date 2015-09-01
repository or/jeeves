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


def schedule_build(project, branch=None, metadata=None):
    build = Build.objects.create(project=project, branch=branch,
                                 creation_time=timezone.now())
    build.set_metadata(metadata)
    build.status = Build.Status.SCHEDULED
    build.save()

    start_build.delay(build.id)


@shared_task
def start_build(build_pk):
    build = Build.objects.get(pk=build_pk)
    build.log_file.save('build-{:05d}-{:05d}.log'.format(build.project.id,
                                                         build.build_id),
                        File(StringIO()))
    build.status = Build.Status.RUNNING
    build.start_time = timezone.now()
    build.save()

    script_context = dict(
        branch=build.branch,
        metadata=build.get_metadata(),
        build_id=build.id,
        build_url=build.get_external_url()
    )

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
