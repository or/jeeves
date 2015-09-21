
from flowdock import Flowdock

from jeeves.notification.models import NotificationTarget, NotificationMetadata


def notify(build, message):
    for notification_target in build.project.notificationtarget_set.all():
        if notification_target.type == NotificationTarget.Type.FLOWDOCK:
            notify_flowdock(
                notification_target.token,
                notification_target.channel,
                build,
                message)


def notify_flowdock(token, channel, build, message):
    notification_metadata, unused_created = \
        NotificationMetadata.objects.get_or_create(
            build=build, type=NotificationTarget.Type.FLOWDOCK)

    if notification_metadata.data:
        thread_id = notification_metadata.data.get('thread_id')
    else:
        thread_id = None

    flowdock = Flowdock(token=token)
    msg = flowdock.message(channel, message, thread_id=thread_id)
    if not notification_metadata.data:
        notification_metadata.data = msg
        notification_metadata.save()
