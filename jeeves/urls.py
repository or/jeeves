from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login, logout

from jeeves.core import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url('^$', views.IndexView.as_view()),
    url('^builds/?$',
        login_required(views.BuildListView.as_view()),
        name="build-list"),
    url('^builds/(?P<pk>\d+)/?$',
        login_required(views.BuildDetailView.as_view()),
        name="build-view"),
    url('^login/?$', login, name='login',
        kwargs={'template_name': 'login.html'}),
    url('^logout/?$', logout, name='logout'),
    url('^github-webhook/?', views.GithubWebhookView.as_view()),
]
