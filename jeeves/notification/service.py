
from flowdock import Flowdock

from jeeves.notification.models import NotificationTarget


def notify(build, message):
    for notification_target in build.project.notificationtarget_set.all():
        if notification_target.type == NotificationTarget.Type.FLOWDOCK:
            notify_flowdock(
                notification_target.token,
                notification_target.channel,
                build,
                message)


def notify_flowdock(token, channel, build, message):
    flowdock = Flowdock(token=token)
    flowdock.message(channel, message)
