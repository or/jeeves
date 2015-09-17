from django.contrib import admin

from .models import NotificationTarget

admin.site.register(NotificationTarget)


class NotificationTargetInline(admin.TabularInline):
    model = NotificationTarget
    extra = 0
