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

        message = {}

        log_offset = kwargs['log_offset']
        log = build.get_log()
        new_log_data = log[log_offset:]
        new_log_offset = len(log)
        if not new_log_data:
            return

        message['log_data'] = new_log_data
        message['log_offset'] = new_log_offset

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
