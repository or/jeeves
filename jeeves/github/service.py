import re
from multiprocessing import Process

from django.conf import settings

from .models import GithubWebhookMatch, GithubRepository

from jeeves.core.service import start_build


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
