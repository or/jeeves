import hmac
import json
from hashlib import sha1
from multiprocessing import Process

from django.conf import settings
from django.http.response import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, View

from jeeves.core.models import Build, Project
from jeeves.core.service import handle_push_hook_request


class ProjectListView(ListView):
    model = Project
    template_name = "project_list.html"

    def get_queryset(self):
        queryset = super(ProjectListView, self).get_queryset()
        return queryset.order_by('name')


class BuildListView(ListView):
    model = Build
    template_name = "build_list.html"

    def get_queryset(self):
        self.project = \
            get_object_or_404(Project, slug=self.kwargs['project_slug'])
        queryset = super(BuildListView, self).get_queryset()
        return queryset.filter(project=self.project).order_by('-build_id')

    def get_context_data(self, *args, **kwargs):
        context = super(BuildListView, self).get_context_data(*args, **kwargs)
        context['last_build'] = self.get_queryset().first()
        context['project'] = self.project
        return context


class BuildDetailView(DetailView):
    model = Build
    template_name = "build_detail.html"

    def get_queryset(self):
        self.project = \
            get_object_or_404(Project, slug=self.kwargs['project_slug'])
        queryset = Build.objects.all()
        return queryset.filter(project=self.project,
                               build_id=self.kwargs['build_id'])

    def get_object(self, queryset=None):
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj


class GithubWebhookView(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(GithubWebhookView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        start_build("test")
        return HttpResponse("OK")

    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body.decode())

        if request.META.get('HTTP_X_GITHUB_EVENT') == "ping":
            return HttpResponse('Hi!')

        if request.META.get('HTTP_X_GITHUB_EVENT') != "push":
            response = HttpResponse()
            response.status_code = 403
            return response

        signature = request.META.get('HTTP_X_HUB_SIGNATURE').split('=')[1]
        secret = settings.GITHUB_HOOK_SECRET
        if isinstance(secret, str):
            secret = secret.encode()

        mac = hmac.new(secret, msg=request.body, digestmod=sha1)
        if not hmac.compare_digest(mac.hexdigest(), signature):
            response = HttpResponse()
            response.status_code = 403
            return response

        p = Process(target=handle_push_hook_request, args=(payload,))
        p.start()

        return HttpResponse("OK")
