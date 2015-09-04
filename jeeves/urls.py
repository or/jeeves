from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import login, logout

import jeeves.core.urls
import jeeves.github.urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url('^login/$', login, name='login',
        kwargs={'template_name': 'login.html'}),
    url('^logout/$', logout, name='logout',
        kwargs={'next_page': '/'}),

    url(r'^github-webhook/', include(jeeves.github.urls)),
    url(r'^', include(jeeves.core.urls)),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
