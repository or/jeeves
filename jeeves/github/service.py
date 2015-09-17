import re

from github import Github

from django.conf import settings

from jeeves.core.models import Job, JobDescription
from jeeves.core.service import schedule_new_build
from jeeves.github.models import GithubWebhookMatch, GithubRepository


def match_to_projects(payload):
    branch = payload['ref']
    if branch.startswith('refs/tags/'):
        # ignore tag pushes
        return [], None

    if branch.startswith('refs/heads/'):
        branch = branch[len('refs/heads/'):]
    try:
        repository = GithubRepository.objects.get(
            name=payload['repository']['full_name'])
    except GithubRepository.DoesNotExist:
        return [], None

    projects = set()
    excludes = set()
    for config in GithubWebhookMatch.objects.filter(repository=repository):
        if not re.match(config.branch_match, branch):
            continue

        if config.exclude:
            excludes.add(config.project)
        else:
            projects.add(config.project)

    return list(projects - excludes), repository


def handle_push_hook_request(payload):
    branch = payload['ref']
    if branch.startswith('refs/tags/'):
        # ignore tag pushes
        return

    if branch.startswith('refs/heads/'):
        branch = branch[len('refs/heads/'):]

    commit = payload['head_commit']['id']
    projects, repository = match_to_projects(payload)
    reason = "GitHub push"
    for project in projects:
        schedule_new_build(project,
                           repository=repository.name, branch=branch,
                           metadata=payload, reason=reason,
                           commit=commit)


def report_status_for_job(job):
    metadata = job.build.metadata
    if not metadata:
        return

    try:
        job_description = JobDescription.objects.get(
            project=job.build.project, name=job.name)
    except JobDescription.DoesNotExist:
        return

    if not job_description.report_result:
        return

    token = getattr(settings, 'GITHUB_ACCESS_TOKEN', None)
    if not token:
        return

    if job.result == Job.Result.SUCCESS:
        status = 'success'
    else:
        status = 'error'

    github = Github('', token)
    repo = github.get_repo(metadata['repository']['full_name'])
    commit = repo.get_commit(metadata['head_commit']['id'])
    commit.create_status(
        status,
        target_url=job.build.get_external_url(),
        description=job.result_details,
        context='Jeeves {}.{}'.format(job.build.project.slug, job.name)
    )
