#!/usr/bin/env python
import json
import requests


class Flowdock:
    def __init__(self, token=None, email=None, password=None,
                 endpoint='api.flowdock.com'):
        self.email = email or token
        self.password = password or ''
        self.endpoint_url = endpoint
        self.api_endpoint = 'https://{email}:{password}@{url}' \
            .format(email=self.email, password=self.password,
                    url=self.endpoint_url)

    def message(self, flow, message, tags=None, thread_id=None):
        if not tags:
            tags = []

        data = {'content': message, 'event': 'message', 'tags': tags}
        if thread_id:
            data['thread_id'] = thread_id

        response = requests.post(
            self.api_endpoint + '/flows/{}/messages'.format(flow),
            data=json.dumps(data),
            headers={'content-type': 'application/json'})

        return response.json()

    def update_message(self, flow, message_id, message, tags=None):
        data = {'content': message}
        if tags:
            data['tags'] = tags

        response = requests.put(
            self.api_endpoint +
            '/flows/{}/messages/{}'.format(flow, message_id),
            data=json.dumps(data),
            headers={'content-type': 'application/json'})

        return response.json()
