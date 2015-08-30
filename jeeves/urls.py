from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login, logout

import jeeves.github.urls
from jeeves.core import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^github-webhook/?', include(jeeves.github.urls)),

    url('^login/?$', login, name='login',
        kwargs={'template_name': 'login.html'}),
    url('^logout/?$', logout, name='logout'),

    url('^$',
        login_required(views.ProjectListView.as_view()),
        name="project-list"),

    url('^(?P<project_slug>[^/]+)/?$',
        login_required(views.BuildListView.as_view()),
        name="build-list"),

    url('^(?P<project_slug>[^/]+)/(?P<build_id>\d+)/?$',
        login_required(views.BuildDetailView.as_view()),
        name="build-view"),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
