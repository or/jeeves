import os
import select
import stat
import subprocess
import sys
import tempfile
import traceback
from io import StringIO

import jinja2
from celery import shared_task

from django.core.files import File
from django.utils import timezone

from jeeves.core.models import Build, BuildSource, Job
from jeeves.core.signals import (build_started, build_finished,
                                 job_started, job_finished)
from jeeves.util import SilentUndefined


def schedule_build(build):
    build.status = Build.Status.SCHEDULED
    build.save()

    start_build.delay(build.id)


def cancel_build(build):
    build.status = Build.Status.CANCELLED
    build.save()


def schedule_new_build(project, repository=None, branch=None,
                       metadata=None, reason=None, commit=None):
    build = Build.objects.create(project=project, repository=repository,
                                 branch=branch, reason=reason, commit=commit,
                                 metadata=metadata or {})
    schedule_build(build)

    return build


def copy_and_schedule_new_build(build, user=None):
    reason = "re-build #{}".format(build.build_id)
    if user:
        reason += ' by {}'.format(user.username)

    new_build = Build.objects.create(
        project=build.project, repository=build.repository, branch=build.branch,
        metadata=build.metadata, reason=reason, commit=build.commit)

    BuildSource.objects.create(build=new_build, source=build, user=user)

    schedule_build(new_build)

    return new_build


def start_job(build, job_description):
    job = Job(build=build, name=job_description.name)
    job.status = Job.Status.RUNNING
    job.log_file.save('build-{:05d}-{:05d}-{}.log'
                      .format(build.project.id,
                              build.build_id,
                              job_description.name),
                      File(StringIO()))
    job.save()

    job_started.send_robust('core', job=job)

    return job


def finish_job(job, result, result_details=None):
    job.status = Job.Status.FINISHED
    job.result = result
    job.result_details = result_details
    job.end_time = timezone.now()
    job.save()

    job_finished.send_robust('core', job=job)


def finish_build(build, result, result_details=None):
    build.status = Build.Status.FINISHED
    build.result = result
    build.result_details = result_details
    build.end_time = timezone.now()

    for job in build.job_set.filter(status=Job.Status.RUNNING):
        finish_job(job, Job.Result.ERROR, "build error")

    build.save()

    build_finished.send_robust('core', build=build)


@shared_task
def start_build(build_pk):
    build = Build.objects.get(pk=build_pk)
    if build.status != Build.Status.SCHEDULED:
        # if this build is not scheduled anymore, then ignore this task
        return

    if build.project.blocking_key_template:
        build.blocking_key = \
            jinja2.Template(build.project.blocking_key_template,
                            undefined=SilentUndefined) \
            .render(build.get_script_context())
        blocking_build = Build.objects.filter(
            project=build.project,
            blocking_key=build.blocking_key,
            build_id__lt=build.build_id
        ).exclude(
            status__in=(Build.Status.CANCELLED, Build.Status.FINISHED)
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

    try:
        run_build(build)
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        exception_data = traceback.format_exception(
            exc_type, exc_value, exc_traceback)
        # new lines are included in each element
        finish_build(build, Build.Result.ERROR, ''.join(exception_data))


class LineReader(object):

    def __init__(self, fd):
        self._fd = fd
        self._buf = b''

    def fileno(self):
        return self._fd

    def readlines(self):
        data = os.read(self._fd, 409600)
        if not data:
            # EOF
            return None

        self._buf += data
        if b'\n' not in data:
            return []

        tmp = self._buf.split(b'\n')
        lines, self._buf = tmp[:-1], tmp[-1]
        return lines


def run_build(build):
    build.status = Build.Status.RUNNING
    build.start_time = timezone.now()
    build.save()

    build_started.send_robust('core', build=build)

    known_jobs = set()
    dependencies = {}
    for jd in build.project.jobdescription_set.all():
        known_jobs.add(jd.name.lower())
        dependencies[jd.name.lower()] = \
            [x.strip().lower() for x in jd.dependencies.split(',') if x.strip().lower()] \
            if jd.dependencies else []

    result_map = {}
    all_passed = True
    jobs_to_do = list(build.project.jobdescription_set.order_by('id'))
    while jobs_to_do:
        jobs_left_to_do = []
        for job_description in jobs_to_do:
            has_unmet_dependencies = False
            for dependency in dependencies[job_description.name.lower()]:
                if dependency in known_jobs and dependency not in result_map:
                    has_unmet_dependencies = True
                    break

            if has_unmet_dependencies:
                jobs_left_to_do.append(job_description)
                continue

            job = start_job(build, job_description)

            failed_dependencies = []
            unknown_dependencies = []
            with open(job.log_file.path, 'a') as log_file:
                for dependency in dependencies[job_description.name.lower()]:
                    if dependency not in known_jobs:
                        log_file.write(
                            "dependency '{}' unknown, not running '{}'\n"
                            .format(dependency, job_description.name))
                        unknown_dependencies.append(dependency)
                    elif result_map[dependency].result == Job.Result.FAILURE:
                        log_file.write(
                            "dependency '{}' failed, not running '{}'\n"
                            .format(dependency, job_description.name))
                        failed_dependencies.append(dependency)

            if failed_dependencies or unknown_dependencies:
                all_passed = False

                info = []
                if failed_dependencies:
                    info.append(
                        'failed: ' + ', '.join(failed_dependencies))

                if unknown_dependencies:
                    info.append(
                        'unknown: ' + ', '.join(unknown_dependencies))

                finish_job(job, Job.Result.FAILURE, '; '.join(info))

                result_map[job_description.name.lower()] = job
                continue

            (fd, file_path) = tempfile.mkstemp(suffix='.sh', prefix='tmp')
            script = job_description.script
            script = jinja2.Template(script, undefined=SilentUndefined) \
                .render(build.get_script_context())
            if not script.startswith('#!/'):
                os.write(fd, b"#!/bin/bash -e\n")

            os.write(fd, script.replace('\r', '\n').encode('utf-8'))
            os.close(fd)

            st = os.stat(file_path)
            os.chmod(file_path, st.st_mode | stat.S_IEXEC)

            env_removals = ['DJANGO_SETTINGS_MODULE', 'VIRTUAL_ENV',
                            'CD_VIRTUAL_ENV']
            env = dict(os.environ)
            for env_entry in env_removals:
                if env_entry in env:
                    env.pop(env_entry)

            out = open(job.log_file.path, 'wb')

            p = subprocess.Popen(
                [file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env)

            stderr = ''
            proc_stdout = LineReader(p.stdout.fileno())
            proc_stderr = LineReader(p.stderr.fileno())
            readable = [proc_stdout, proc_stderr]
            while readable:
                ready = select.select(readable, [], [], 1.0)[0]
                if not ready:
                    continue

                for stream in ready:
                    lines = stream.readlines()
                    if lines is None:
                        # got EOF on this stream
                        readable.remove(stream)
                        continue

                    for line in lines:
                        line += b'\n'

                        if stream == proc_stderr:
                            out.write(b'__stderr: ' + line)
                            stderr += line.decode('utf-8')
                        else:
                            out.write(line)

                        out.flush()

            for stream in [proc_stdout, proc_stderr]:
                if not stream._buf:
                    continue

                line = stream._buf + b'\n'
                if stream == proc_stderr:
                    out.write(b'__stderr: ' + line)
                    stderr += line.decode('utf-8')
                else:
                    out.write(line)

                out.flush()

            out.close()
            p.wait()
            result = p.returncode

            if not result:
                finish_job(job, Job.Result.SUCCESS, '')
            else:
                finish_job(job, Job.Result.FAILURE, stderr)
                all_passed = False

            result_map[job_description.name.lower()] = job

        if jobs_to_do == jobs_left_to_do:
            # this shouldn't happen, but to avoid an endless loop,
            # let's fail hard here
            raise Exception('iteration over jobs_to_do made no progress: {}'
                            .format(jobs_to_do))

        jobs_to_do = jobs_left_to_do

    if all_passed:
        result = Build.Result.SUCCESS
    else:
        result = Build.Result.FAILURE

    finish_build(build, result)
