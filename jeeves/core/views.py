from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, ListView

from jeeves.core.models import Build, Project


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
        context = super(BuildDetailView, self).get_context_data(*args, **kwargs)
        context['project'] = self.project
        return context
