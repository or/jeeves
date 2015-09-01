from datetime import timedelta

from swampdragon import route_handler
from swampdragon.pubsub_providers.data_publisher import publish_data
from tornado.ioloop import PeriodicCallback

from django.db.models import Q
from django.template.loader import get_template
from django.utils import timezone

from jeeves.core.models import Build

pcb = None
previous_build_list_data = None
last_timestamp = None
header_cache = {}


class BuildChangesRouter(route_handler.BaseRouter):
    route_name = 'build-changes'
    valid_verbs = ['subscribe', 'get_detail_header']

    def get_subscription_channels(self, **kwargs):
        get_changed_build_list_rows()
        return ['build-list']

    def get_detail_header(self, **kwargs):
        global header_cache
        build_pk = kwargs['id']
        build = Build.objects.get(pk=build_pk)
        template = get_template("partials/build_detail_header.html")
        html = template.render({'build': build})

        message = {}
        if header_cache.get(build_pk) != html:
            message['html'] = html
            header_cache[build_pk] = html

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
    global pcb, last_timestamp, previous_build_list_data

    if pcb is None:
        pcb = PeriodicCallback(get_changed_build_list_rows, 1000)
        pcb.start()

    data = {}
    now = timezone.now()
    if not last_timestamp:
        last_timestamp = now - timedelta(seconds=3600)

    for build in Build.objects.filter(
        Q(status__in=(Build.Status.SCHEDULED, Build.Status.RUNNING)) |
        Q(modified_time__gt=last_timestamp)
    ):
        template = get_template("partials/build_list_row.html")
        progress_html = template.render({'build': build})
        data[build.id] = {'html': progress_html}

    last_timestamp = now

    diff_data = []
    refresh_needed = False
    for key, value in data.items():
        if (previous_build_list_data is not None and
                key not in previous_build_list_data):
            refresh_needed = True
            continue

        if (previous_build_list_data is not None and
                key in previous_build_list_data and
                previous_build_list_data[key] != value):
            entry = dict(value)
            entry['id'] = key
            diff_data.append(entry)

    previous_build_list_data = data

    message = {'build_list_changes': diff_data}
    if refresh_needed:
        message['refresh_needed'] = True

    publish_data('build-list', message)
