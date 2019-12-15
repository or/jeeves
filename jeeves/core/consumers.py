import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from jeeves.core.models import Build

def all_builds_channel():
    return 'all-build-change'

def project_builds_channel(project_id):
    return 'project-{}-builds'.format(project_id)

def build_channel(build_id):
    return 'build-change-{}'.format(build_id)

class BuildListChangesConsumer(WebsocketConsumer):
    def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.group_name = project_builds_channel(self.project_id)

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def build_list_update(self, event):
        self.send(text_data=json.dumps(event['data']))


class BuildChangesConsumer(WebsocketConsumer):
    def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.build_id = self.scope['url_route']['kwargs']['build_id']
        self.group_name = build_channel(self.build_id)

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'get_latest_log':
            build = Build.objects.get(pk=self.build_id)
            message = get_log_change_message(build, offsets=data['offsets'])

            if message:
                self.send(text_data=json.dumps(message))

    def build_update(self, event):
        self.send(text_data=json.dumps(event['data']))

    def job_update(self, event):
        self.send(text_data=json.dumps(event['data']))


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
