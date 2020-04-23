import random

import jinja2

from flowdock import Flowdock

from jeeves.core.models import Build
from jeeves.notification.models import NotificationTarget, NotificationMetadata
from jeeves.util import SilentUndefined


class Event:
    BUILD_STARTED = "build_started"
    BUILD_FINISHED = "build_finished"
    JOB_STARTED = "job_started"
    JOB_FINISHED = "job_finished"


EMOJI_THEMES = {
    'religion': {
        'start': 'pray', 'success': 'angel', 'failure': 'japanese_ogre'
    },
    'science': {
        'start': 'rocket', 'success': 'fireworks', 'failure': 'boom'
    },
    'doom': {
        'start': 'suspect', 'success': 'godmode', 'failure': 'feelsgood'
    },
    'meme': {
        'start': 'octocat', 'success': 'shipit', 'failure': 'trollface'
    },
    'moon': {
        'start': 'first_quarter_moon', 'success': 'full_moon',
        'failure': 'new_moon'
    },
    'cats': {
        'start': 'smirk_cat', 'success': 'heart_eyes_cat',
        'failure': 'crying_cat_face'
    },
    'monkey': {
        'start': 'see_no_evil', 'success': 'hear_no_evil',
        'failure': 'speak_no_evil'
    },
    'hands': {
        'start': 'wave', 'success': 'thumbsup', 'failure': 'thumbsdown'
    },
    'bank': {
        'start': 'bar_chart', 'success': 'chart_with_upwards_trend',
        'failure': 'chart_with_downwards_trend'
    },
    'cars': {
        'start': 'vertical_traffic_light', 'success': 'blue_car',
        'failure': 'fire_engine'
    },
    'race': {
        'start': 'traffic_light', 'success': 'checkered_flag',
        'failure': 'flags'
    },
    'smiley1': {
        'start': 'open_mouth', 'success': 'smiley', 'failure': 'angry'
    },
    'smiley2': {
        'start': 'relaxed', 'success': 'sunglasses', 'failure': 'flushed'
    },
    'smiley3': {
        'start': 'no_mouth', 'success': 'relieved', 'failure': 'anguished'
    },
    'hearts': {
        'start': 'yellow_heart', 'success': 'green_heart',
        'failure': 'broken_heart'
    },
}


def get_emoji(theme, event):
    global EMOJI_THEMES
    return ':' + EMOJI_THEMES[theme][event] + ':'


def get_emoji_theme():
    global EMOJI_THEMES
    return random.choice(list(EMOJI_THEMES.keys()))


def notify(event, build=None, job=None):
    if not build:
        build = job.build

    for notification_target in build.project.notificationtarget_set.all():
        if not notification_target.enabled:
            continue

        if notification_target.type == NotificationTarget.Type.FLOWDOCK:
            notify_flowdock(
                notification_target.token,
                notification_target.channel,
                event,
                build=build, job=job)


def make_flowdock_message(event, build=None, job=None):
    if not build:
        build = job.build

    message_map = {
        Event.BUILD_STARTED:
            "{{ theme.start }} {{ build_url }} {{ branch }}",

        Event.BUILD_FINISHED: {
            Build.Result.SUCCESS:
                "{{ theme.success }} {{ build_url }} {{ branch }}",
            Build.Result.FAILURE: (
                "{{ theme.failure }} {{ build_url }} {{ branch }}"
                "{{ errors }}"
            ),
            Build.Result.ERROR:
            "{{ theme.failure }} {{ build_url }} {{ branch }}{{ errors }}",
        }
    }
    tag_map = {
        Event.BUILD_STARTED: ['begin'],
        Event.BUILD_FINISHED: {
            Build.Result.SUCCESS: ['success'],
            Build.Result.FAILURE: ['failure'],
            Build.Result.ERROR: ['error'],
        }
    }

    if event not in message_map:
        return

    if event == Event.BUILD_FINISHED:
        if build.result not in message_map[event]:
            return

        template = message_map[event][build.result]
        tags = tag_map.get(event, {}).get(build.result, None)
    else:
        template = message_map[event]
        tags = tag_map.get(event, None)

    notification_metadata, unused_created = \
        NotificationMetadata.objects.get_or_create(
            build=build, defaults={'data': {}})

    context = build.get_script_context()
    if 'theme' in notification_metadata.data:
        context['theme'] = {
            k: get_emoji(notification_metadata.data['theme'], k)
            for k in ['start', 'success', 'failure']
        }

    context['errors'] = ''
    errors = [(x.name, x.result_details) for x in build.get_jobs() if x.result_details]
    if build.result_details:
        errors = [('error', build.result_details)] + errors

    if errors:
        context['errors'] = \
            '\n\n' + \
            '\n\n'.join('* {}:\n\n      {}'.format(x[0], x[1].replace('\n', '\n      '))
                        for x in errors)

    message = jinja2.Template(template, undefined=SilentUndefined) \
        .render(context)

    return message, tags


def notify_flowdock(token, channel, event, build=None, job=None):
    if not build:
        build = job.build

    notification_metadata, unused_created = \
        NotificationMetadata.objects.get_or_create(
            build=build, defaults={'data': {}})

    if not notification_metadata.data:
        notification_metadata.data = {}

    if 'theme' not in notification_metadata.data:
        notification_metadata.data['theme'] = get_emoji_theme()

    if 'flowdock' in notification_metadata.data:
        thread_id = notification_metadata.data['flowdock'].get('thread_id')
    else:
        thread_id = None

    notification_metadata.save()

    flowdock = Flowdock(token=token)

    flowdock_message = make_flowdock_message(event, build=build, job=job)
    if not flowdock_message:
        return

    message, tags = flowdock_message

    msg = flowdock.message(channel, message, tags=tags, thread_id=thread_id)
    if 'flowdock' not in notification_metadata.data:
        notification_metadata.data['flowdock'] = msg
        notification_metadata.save()
