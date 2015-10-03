from swampdragon import route_handler
from swampdragon.pubsub_providers.data_publisher import publish_data

from django.template.loader import get_template

from jeeves.core.models import Build, Project


class BuildChangesRouter(route_handler.BaseRouter):
    route_name = 'build-changes'
    valid_verbs = ['subscribe', 'get_latest_log']

    def get_subscription_channels(self, **kwargs):
        channels = ['all-build-change']
        for project in Project.objects.all():
            channels.append('{}-build-change'.format(project.id))

        build_pk = kwargs.get('id')
        if build_pk:
            channels.append('build-change-{}'.format(build_pk))

        return channels

    def get_latest_log(self, **kwargs):
        build_pk = kwargs.get('id')
        if not build_pk:
            return

        build = Build.objects.get(pk=build_pk)
        message = get_log_change_message(build, offsets=kwargs.get('offsets'))

        if message:
            self.send(message)

route_handler.register(BuildChangesRouter)


def send_build_change(build):
    template = get_template("partials/build_list_row.html")
    row_html = template.render({'build': build})
    publish_data('all-build-change', {'id': build.id, 'row_html': row_html})
    publish_data('{}-build-change'.format(build.project.id),
                 {'id': build.id, 'row_html': row_html})

    template = get_template("partials/build_detail_header.html")
    details_html = template.render({'build': build})
    publish_data('build-change-{}'.format(build.id), {'id': build.id, 'details_html': details_html})


def send_job_change(job):
    build = job.build
    template = get_template("partials/job_list.html")
    jobs_html = template.render({'build': build})
    publish_data('build-change-{}'.format(build.id), {'id': build.id, 'jobs_html': jobs_html})


def get_log_change_message(build, offsets=None, initial=False):
    if offsets is None:
        offsets = {}

    message = {'jobs': [], 'data': {}, 'offsets': {}}
    got_changes = False
    for job in build.get_jobs():
        offset = offsets.get(job.name, 0)
        log_data, new_offset = job.get_log(offset=offset)
        message['jobs'].append(job.name)

        # if there is no new data and we already had an offset for it,
        # then the client knows about it and we don't have to send an update
        if not log_data and job.name in offsets:
            continue

        message['data'][job.name] = log_data
        message['offsets'][job.name] = new_offset
        got_changes = True

    if got_changes or initial:
        return message

    return None
