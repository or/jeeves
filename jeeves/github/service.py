import fnmatch

from .models import GithubConfig, GithubRepository

from jeeves.core.service import start_build


def match_to_projects(payload):
    branch = payload['ref'][len('refs/heads/'):]
    try:
        repository = GithubRepository.objects.get(
            name=payload['repository']['full_name'])
    except GithubRepository.DoesNotExist:
        return []

    projects = set()
    for config in GithubConfig.objects.filter(repository=repository):
        if fnmatch.fnmatch(branch, config.branch_match):
            projects.add(config.project)

    return list(projects)


def handle_push_hook_request(payload):
    branch = payload['ref'][len('refs/heads/'):]
    projects = match_to_projects(payload)
    for project in projects:
        start_build(project, branch, metadata=payload)
