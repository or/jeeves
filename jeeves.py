#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import hmac
import ipaddress
import json
import os
import re
import sys
import subprocess
from datetime import datetime
from hashlib import sha1

import requests

from flask import Flask, abort, request
from flask.ext.sqlalchemy import SQLAlchemy

sys.path.append(os.path.dirname(__file__))

app = Flask(__name__)
app.config.from_pyfile('settings.py')
db = SQLAlchemy(app)


class Build(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instance = db.Column(db.String(256))
    branch = db.Column(db.String(256))
    started = db.Column(db.DateTime)
    ended = db.Column(db.DateTime)

    def __init__(self, instance, branch=None):
        self.instance = instance
        self.branch = branch or instance

    def __repr__(self):
        return '<Build #{}:{}>'.format(self.id, self.instance)

    def start(self):
        self.started = datetime.now()

    def end(self):
        self.ended = datetime.now()


@app.route("/github-webhook", methods=['GET', 'POST'])
def github_webhook():
    """
    Based on https://github.com/razius/github-webhook-handler
    """
    if request.method == 'GET':
        build = Build('test-instance')
        db.session.add(build)

        build.start()
        db.session.commit()

        build.end()
        db.session.commit()
        return 'OK'
    elif request.method == 'POST':
        # Store the IP address of the requester
        request_ip = ipaddress.ip_address(request.remote_addr)

        allowed_networks = []
        allowed_networks += ['127.0.0.1/24']
        allowed_networks += requests.get('https://api.github.com/meta').json()['hooks']

        # check if the request came from an allowed network
        for block in allowed_networks:
            if ipaddress.ip_address(request_ip) in ipaddress.ip_network(block):
                # the remote_addr is within an allowed network
                break
        else:
            abort(403)

        if request.headers.get('X-GitHub-Event') == "ping":
            return json.dumps({'msg': 'Hi!'})

        if request.headers.get('X-GitHub-Event') != "push":
            return json.dumps({'msg': "wrong event type"})

        repos = json.loads(open(REPOS_JSON_PATH, 'r').read())

        payload = json.loads(request.data)
        repo_meta = {
            'name': payload['repository']['name'],
            'owner': payload['repository']['owner']['name'],
        }

        # Try to match on branch as configured in repos.json
        match = re.match(r"refs/heads/(?P<branch>.*)", payload['ref'])
        if match:
            repo_meta['branch'] = match.groupdict()['branch']
            repo = repos.get(
                '{owner}/{name}/branch:{branch}'.format(**repo_meta), None)

            # Fallback to plain owner/name lookup
            if not repo:
                repo = repos.get('{owner}/{name}'.format(**repo_meta), None)

        if repo and repo.get('path', None):
            # Check if POST request signature is valid
            key = repo.get('key', None)
            if key:
                signature = request.headers.get('X-Hub-Signature').split(
                    '=')[1]
                if type(key) == unicode:
                    key = key.encode()
                mac = hmac.new(key, msg=request.data, digestmod=sha1)
                if not compare_digest(mac.hexdigest(), signature):
                    abort(403)

            if repo.get('action', None):
                for action in repo['action']:
                    subp = subprocess.Popen(action, cwd=repo['path'])
                    subp.wait()
        return 'OK'


def run_server(args):
    global jeeves_options, db
    jeeves_options = args

    app.debug |= args.debug
    if args.port:
        app.port = args.port

    app.host = '0.0.0.0'

    if args.create_db:
        db.create_all()

    app.run()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--create-db', action='store_true', help='create all tables')
    parser.add_argument('--debug', action='store_true', help='turn on debug mode')
    parser.add_argument('-p', '--port', type=int, help='the port to listen on')
    parser.add_argument('-f', '--config-file', type=str, help='the config file to use')

    args = parser.parse_args()

    run_server(args)


if __name__ == "__main__":
    main()
