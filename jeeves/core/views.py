import json

from django.contrib import messages
from django.http.response import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, ListView

from jeeves.core.models import Build, Project
from jeeves.core.service import cancel_build, copy_and_schedule_new_build
from jeeves.core.routers import build_info


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
        return queryset.filter(project=self.project) \
            .select_related('project').order_by('-build_id')[:20]

    def get_context_data(self, *args, **kwargs):
        context = super(BuildListView, self).get_context_data(*args, **kwargs)
        context['project'] = self.project
        context['all_builds'] = mark_safe(
            json.dumps(map(build_info, Build.objects.order_by('-build_id'))))
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

    def get_context_data(self, *args, **kwargs):
        context = super(BuildDetailView, self) \
            .get_context_data(*args, **kwargs)
        context['project'] = self.project
        return context


class BuildCopyScheduleView(BuildDetailView):
    def get(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        build = self.get_object()
        new_build = copy_and_schedule_new_build(build, user=request.user)

        messages.add_message(
            request, messages.SUCCESS,
            'Scheduled build #{} based on build #{}.'.format(
                new_build.build_id, build.build_id))

        template = get_template("partials/messages.html")
        data = {'messages_html': template.render(RequestContext(request))}

        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        return HttpResponse(status_code=403)


class BuildCancelView(BuildDetailView):
    def get(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        build = self.get_object()
        cancel_build(build)

        messages.add_message(
            request, messages.SUCCESS,
            'Cancelled build #{}.'.format(build.build_id))

        template = get_template("partials/messages.html")
        data = {'messages_html': template.render(RequestContext(request))}

        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        return HttpResponse(status_code=403)


class BuildLogView(BuildDetailView):
    def get(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        build = self.get_object()
        response = HttpResponse(content_type="text/plain")
        response.write(build.get_log())
        return response

    def post(self, request, *args, **kwargs):
        return HttpResponse(status_code=403)
