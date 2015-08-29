from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login

from jeeves.core import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url('^$', views.IndexView.as_view()),
    url('^builds/?$', views.BuildListView.as_view(), name="build-list"),
    url('^builds/(?P<pk>\d+)/?$', views.BuildDetailView.as_view(),
        name="build-view"),
    url('^login/?$', login, name='login',
        kwargs={'template_name': 'login.html'}),
    url('^github-webhook/?', views.GithubWebhookView.as_view()),
]
