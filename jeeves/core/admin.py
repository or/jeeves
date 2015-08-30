from django.contrib import admin

from .models import Build, Project

from jeeves.github.admin import GithubConfigInline


class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

    inlines = [
        GithubConfigInline
    ]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Build)
