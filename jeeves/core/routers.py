from swampdragon import route_handler
from swampdragon.pubsub_providers.data_publisher import publish_data
from toolz import merge

from django.template.loader import get_template
from django.utils import timezone

from jeeves.core.models import Build, Project

last_update_time = {}


class BuildChangesRouter(route_handler.BaseRouter):
    route_name = 'build-changes'
    valid_verbs = ['subscribe', 'get_detail_header', 'get_all_builds']

    def get_subscription_channels(self, **kwargs):
        channels = ['build-change-all']
        for project in Project.objects.all():
            channels.append('build-update-json-{}'.format(project.id))

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
        log = build.get_log()
        new_log_data = log[log_offset:]
        new_log_offset = len(log)
        if new_log_data:
            message['log_data'] = new_log_data
            message['log_offset'] = new_log_offset

        if message:
            self.send(message)

    def get_all_builds(self, **kwargs):
        self.send({'builds': map(build_info, Build.objects.order_by('-build_id'))})


route_handler.register(BuildChangesRouter)


def build_info(build):
    return merge(
        {k: getattr(build, k) for k in [
            'status',
            'result',
            'commit',
            'branch',
            'reason',
        ]},
        {
            'build-id': build.build_id,
            'view-url': build.get_view_url(),
            'branch-url': build.get_branch_link(),
            'schedule-copy-url': build.get_schedule_copy_url(),
            'cancellable?': build.is_cancellable(),
            'age-in-seconds': build.get_age_in_seconds(),
            'estimated-duration': build.get_estimated_time(),
            'duration': build.get_duration(),
            'sender-avatar-url': build.get_metadata().get('sender', {}).get('avatar_url'),
            'sender-html-url': build.get_metadata().get('sender', {}).get('html_url'),
            'sender-login': build.get_metadata().get('sender', {}).get('login')
        }
    )


def send_build_change(build):
    template = get_template("partials/build_list_row.html")
    row_html = template.render({'build': build})
    publish_data('build-update-json-{}'.format(build.project.id), {'change': 'update',
                                                                   'build': build_info(build)})


def send_build_delete(build):
    publish_data('build-update-json-{}'.format(build.project.id), {'change': 'delete',
                                                                   'build-id': build.build_id})
