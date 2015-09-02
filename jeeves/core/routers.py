from datetime import timedelta

from swampdragon import route_handler
from swampdragon.pubsub_providers.data_publisher import publish_data
from tornado.ioloop import PeriodicCallback

from django.template.loader import get_template
from django.utils import timezone

from jeeves.core.models import Build

pcb = None
last_timestamp = None
last_update_time = {}


class BuildChangesRouter(route_handler.BaseRouter):
    route_name = 'build-changes'
    valid_verbs = ['subscribe', 'get_detail_header']

    def get_subscription_channels(self, **kwargs):
        get_changed_build_list_rows()
        return ['build-list']

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

        self.send(message)


route_handler.register(BuildChangesRouter)


def get_changed_build_list_rows():
    global pcb, last_timestamp

    if pcb is None:
        pcb = PeriodicCallback(get_changed_build_list_rows, 1000)
        pcb.start()

    now = timezone.now()
    if not last_timestamp:
        last_timestamp = now - timedelta(seconds=3600)

    diff_data = []
    for build in Build.objects.filter(modified_time__gt=last_timestamp - timedelta(seconds=2)):
        template = get_template("partials/build_list_row.html")
        progress_html = template.render({'build': build})
        diff_data.append({'id': build.id, 'html': progress_html})

    last_timestamp = now

    if diff_data:
        message = {'build_list_changes': diff_data}
        publish_data('build-list', message)
