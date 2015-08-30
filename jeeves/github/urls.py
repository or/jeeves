from django.conf.urls import url

from . import views

urlpatterns = [
    url('^$', views.GithubWebhookView.as_view()),
]
