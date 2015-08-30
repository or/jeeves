from django.contrib import admin

from .models import GithubConfig, GithubRepository

admin.site.register(GithubConfig)
admin.site.register(GithubRepository)


class GithubRepositoryInline(admin.TabularInline):
    model = GithubRepository


class GithubConfigInline(admin.TabularInline):
    model = GithubConfig

    inlines = [
        GithubRepositoryInline
    ]
