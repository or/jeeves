from github import Github
from django.conf import settings

from jeeves.core.models import Job
from jeeves.core.signals import reportable_job_finished


def job_finished_callback(sender, job, details, *args, **kwargs):
    metadata = job.build.get_metadata()
    if not metadata:
        return

    token = getattr(settings, 'GITHUB_ACCESS_TOKEN', None)
    if not token:
        return

    if job.result == Job.Result.SUCCESS:
        status = 'success'
    else:
        status = 'error'

    description = details

    github = Github('', token)
    repo = github.get_repo(metadata['repository']['full_name'])
    commit = repo.get_commit(metadata['head_commit']['id'])
    commit.create_status(
        status,
        target_url=job.build.get_external_url(),
        description=description,
        context='Jeeves {}.{}'.format(job.build.project.slug, job.name)
    )


reportable_job_finished.connect(job_finished_callback)
