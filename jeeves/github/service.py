import re

from github import Github

from django.conf import settings

from .models import GithubWebhookMatch, GithubRepository

from jeeves.core.models import Build
from jeeves.core.service import schedule_build
from jeeves.core.signals import build_finished


def match_to_projects(payload):
    branch = payload['ref'][len('refs/heads/'):]
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
    branch = payload['ref'][len('refs/heads/'):]
    commit = payload['head_commit']['id']
    projects, repository = match_to_projects(payload)
    reason = "triggered by GitHub push"
    for project in projects:
        schedule_build(project,
                       repository=repository.name, branch=branch,
                       metadata=payload, reason=reason,
                       commit=commit)


def build_finished_callback(sender, build, *args, **kwargs):
    metadata = build.get_metadata()
    token = getattr(settings, 'GITHUB_ACCESS_TOKEN', None)
    if not token:
        return

    if build.result == Build.Result.SUCCESS:
        status = 'success'
    else:
        status = 'error'

    description = build.get_duration()

    github = Github('', token)
    repo = github.get_repo(metadata['repository']['full_name'])
    commit = repo.get_commit(metadata['head_commit']['id'])
    commit.create_status(
        status,
        target_url=build.get_external_url(),
        description=description,
        context='Jeeves / ' + build.project.slug
    )

build_finished.connect(build_finished_callback)
