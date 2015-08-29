from jeeves.core.models import Build


def navbar(request):
    return {
        'num_running_builds':
        Build.objects.filter(status=Build.Status.RUNNING).count(),
    }
