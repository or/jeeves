from django.contrib import admin

from .models import Build, Project

from jeeves.github.admin import GithubWebhookMatchInline


class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

    inlines = [
        GithubWebhookMatchInline
    ]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Build)
