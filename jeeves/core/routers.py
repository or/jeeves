from swampdragon import route_handler
from swampdragon.pubsub_providers.data_publisher import publish_data

from django.template.loader import get_template
from django.utils import timezone

from jeeves.core.models import Build, Project

last_update_time = {}


class BuildChangesRouter(route_handler.BaseRouter):
    route_name = 'build-changes'
    valid_verbs = ['subscribe', 'get_detail_header']

    def get_subscription_channels(self, **kwargs):
        channels = ['build-change-all']
        for project in Project.objects.all():
            channels.append('build-change-{}'.format(project.id))

        return channels

    def get_detail_header(self, **kwargs):
        global last_update_time
        build_pk = kwargs['id']
        build = Build.objects.get(pk=build_pk)

        message = {}
        last_timestamp = last_update_time.get(build_pk)
        if not last_timestamp or build.modified_time > last_timestamp:
            template_details = get_template("partials/build_detail_header.html")
            message['details_html'] = template_details.render({'build': build})

        for job in build.get_jobs():
            if not last_timestamp or job.modified_time > last_timestamp:
                # at least one job changed, so update job info
                template_jobs = get_template("partials/job_list.html")
                message['jobs_html'] = template_jobs.render({'build': build})
                break

        last_update_time[build_pk] = timezone.now()

        log_offset = kwargs['log_offset']
        log = build.get_log()
        new_log_data = log[log_offset:]
        new_log_offset = len(log)
        if new_log_data:
            message['log_data'] = new_log_data
            message['log_offset'] = new_log_offset

        if message:
            self.send(message)


route_handler.register(BuildChangesRouter)


def send_build_change(build):
    template = get_template("partials/build_list_row.html")
    row_html = template.render({'build': build})
    publish_data('build-change-all', {'id': build.id, 'row_html': row_html})
    publish_data('build-change-{}'.format(build.project.id),
                 {'id': build.id, 'row_html': row_html})
