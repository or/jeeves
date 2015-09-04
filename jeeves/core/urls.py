from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url('^$',
        login_required(views.ProjectListView.as_view()),
        name="project-list"),

    url('^(?P<project_slug>[^/]+)/$',
        login_required(views.BuildListView.as_view()),
        name="build-list"),

    url('^(?P<project_slug>[^/]+)/(?P<build_id>\d+)/$',
        login_required(views.BuildDetailView.as_view()),
        name="build-view"),

    url('^(?P<project_slug>[^/]+)/(?P<build_id>\d+)/reschedule/$',
        login_required(views.BuildRescheduleView.as_view()),
        name="build-reschedule"),

    url('^(?P<project_slug>[^/]+)/(?P<build_id>\d+)/log/$',
        login_required(views.BuildLogView.as_view()),
        name="build-log"),
]
