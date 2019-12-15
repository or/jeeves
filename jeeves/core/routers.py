from django.urls import re_path

import channels.layers
from asgiref.sync import async_to_sync

from . import consumers

from django.template.loader import get_template

from jeeves.core.models import Build, Project

websocket_urlpatterns = [
    re_path(r'ws/builds/(?P<project_id>\w+)/$', consumers.BuildListChangesConsumer),
    re_path(r'ws/builds/(?P<project_id>\w+)/(?P<build_id>\w+)/$', consumers.BuildChangesConsumer),
]

channel_layer = channels.layers.get_channel_layer()

def publish_data(channel_name, message_type, data):
    async_to_sync(channel_layer.group_send)(channel_name, {
        'type': message_type,
        'data': data,
    })


def send_build_change(build):
    template = get_template("partials/build_list_row.html")
    row_html = template.render({'build': build})
    publish_data(consumers.all_builds_channel(),
                 'build_list_update',
                 {'id': build.id, 'row_html': row_html})
    publish_data(consumers.project_builds_channel(build.project.id),
                 'build_list_update',
                 {'id': build.id, 'row_html': row_html})

    template = get_template("partials/build_detail_header.html")
    details_html = template.render({'build': build})
    publish_data(consumers.build_channel(build.id),
                 'build_update',
                 {'id': build.id, 'details_html': details_html})


def send_job_change(job):
    build = job.build
    template = get_template("partials/job_list.html")
    jobs_html = template.render({'build': build})
    publish_data(consumers.build_channel(build.id),
                 'job_update',
                 {'id': build.id, 'jobs_html': jobs_html})
