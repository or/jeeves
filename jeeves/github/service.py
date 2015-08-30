import re
from multiprocessing import Process

from github import Github

from django.conf import settings

from .models import GithubWebhookMatch, GithubRepository

from jeeves.core.models import Build
from jeeves.core.service import start_build
from jeeves.core.signals import build_finished


def match_to_projects(payload):
    branch = payload['ref'][len('refs/heads/'):]
    try:
        repository = GithubRepository.objects.get(
            name=payload['repository']['full_name'])
    except GithubRepository.DoesNotExist:
        return []

    projects = set()
    excludes = set()
    for config in GithubWebhookMatch.objects.filter(repository=repository):
        if not re.match(config.branch_match, branch):
            continue

        if config.exclude:
            excludes.add(config.project)
        else:
            projects.add(config.project)

    return list(projects - excludes)


def handle_push_hook_request(payload):
    branch = payload['ref'][len('refs/heads/'):]
    projects = match_to_projects(payload)
    for project in projects:
        if getattr(settings, 'SINGLE_THREAD_MODE', False):
            start_build(project, branch, metadata=payload)
            continue

        p = Process(target=start_build,
                    args=(project, branch),
                    kwargs=dict(metadata=payload))
        p.start()


def build_finished_callback(sender, build, metadata, *args, **kwargs):
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
