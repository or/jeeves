from django.contrib import admin

from .models import GithubWebhookMatch, GithubRepository

admin.site.register(GithubWebhookMatch)
admin.site.register(GithubRepository)


class GithubRepositoryInline(admin.TabularInline):
    model = GithubRepository


class GithubWebhookMatchInline(admin.TabularInline):
    model = GithubWebhookMatch
    extra = 0

    inlines = [
        GithubRepositoryInline
    ]
