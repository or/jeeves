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
            template = get_template("partials/build_detail_header.html")
            message['html'] = template.render({'build': build})

        last_update_time[build_pk] = timezone.now()

        log_offset = kwargs['log_offset']
        if build.log_file:
            build.log_file.open()
            build.log_file.seek(log_offset)
            new_log_data = build.log_file.read().decode('utf-8')
            new_log_offset = log_offset + len(new_log_data)
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
