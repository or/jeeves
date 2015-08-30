from django.contrib import admin

from jeeves.core.models import Build, Project


class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Project, ProjectAdmin)
admin.site.register(Build)
