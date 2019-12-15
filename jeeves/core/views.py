import json

from django.contrib import messages
from django.db.models import Case, Count, IntegerField, Q, Sum, When
from django.http.response import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, ListView

from jeeves.core.models import Build, Project
from jeeves.core.service import cancel_build, copy_and_schedule_new_build
from jeeves.core.consumers import get_log_change_message


class ProjectListView(ListView):
    model = Project
    template_name = "project_list.html"

    def get_queryset(self):
        queryset = super(ProjectListView, self).get_queryset()
        return queryset.order_by('name')


class ProjectGraphsView(DetailView):
    model = Project
    slug_url_kwarg = 'project_slug'
    template_name = "project_graphs.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProjectGraphsView, self).get_context_data(*args, **kwargs)
        data = []
        for build in reversed(self.object.build_set.filter(status=Build.Status.FINISHED).order_by('-id')[:20]):
            build_data = {
                'name': '#{}'.format(build.build_id),
                'creation_time': build.creation_time.isoformat(' '),
                'duration': build.get_duration_in_seconds(),
                'duration_display': build.get_duration(),
                'status': build.status,
                'result': build.status,
                'jobs': [],
            }

            for job in build.get_jobs():
                build_data['jobs'].append({
                    'name': job.name,
                    'duration': job.get_duration_in_seconds(),
                    'duration_display': job.get_duration(),
                    'status': job.status,
                    'result': job.result,
                })

            data.append(build_data)

        context['duration_graph_data'] = json.dumps(data)

        data = self.object.build_set.values('branch') \
            .annotate(
                num_total=Count('id'),
                num_succeeded=Sum(
                    Case(When(result=Build.Result.SUCCESS, then=1), output_field=IntegerField())
                ),
                num_failed=Sum(
                    Case(When(~Q(result=Build.Result.SUCCESS), then=1), output_field=IntegerField())
                ),
                ).order_by('-num_total')[:20]
        data = list(data)

        context['builds_per_branch_graph_data'] = json.dumps(data)

        return context


class BuildListView(ListView):
    model = Build
    template_name = "build_list.html"

    def get_queryset(self):
        self.project = \
            get_object_or_404(Project, slug=self.kwargs['project_slug'])
        queryset = super(BuildListView, self).get_queryset()
        return queryset.filter(project=self.project) \
            .select_related(
                'project', 'source',
                'source__user', 'source__source', 'source__source__project'
            ).order_by('-build_id')[:20]

    def get_context_data(self, *args, **kwargs):
        context = super(BuildListView, self).get_context_data(*args, **kwargs)
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

    def get_context_data(self, *args, **kwargs):
        context = super(BuildDetailView, self) \
            .get_context_data(*args, **kwargs)
        context['project'] = self.project
        context['log_data'] = json.dumps(get_log_change_message(
            context['object'], initial=True))
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
        data = {'messages_html': template.render(RequestContext(request).flatten())}

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
        data = {'messages_html': template.render(RequestContext(request).flatten())}

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
