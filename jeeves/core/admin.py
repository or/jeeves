from django.contrib import admin

from .models import Build, Project, JobDescription, Job

from jeeves.github.admin import GithubWebhookMatchInline
from jeeves.notification.admin import NotificationTargetInline


class JobDescriptionInline(admin.TabularInline):
    model = JobDescription
    extra = 0


class ProjectAdmin(admin.ModelAdmin):
    model = Project
    prepopulated_fields = {"slug": ("name",)}

    inlines = [
        JobDescriptionInline,
        GithubWebhookMatchInline,
        NotificationTargetInline,
    ]


class JobInline(admin.TabularInline):
    model = Job
    extra = 0


class BuildAdmin(admin.ModelAdmin):
    model = Build

    inlines = [
        JobInline,
    ]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Build, BuildAdmin)
