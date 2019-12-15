from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django import forms

from jeeves.core.models import Build, JobDescription, Job, Project, UserProfile
from jeeves.github.admin import GithubWebhookMatchInline
from jeeves.notification.admin import NotificationTargetInline


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(UserAdmin):
    inlines = (UserProfileInline,)


class JobDescriptionInlineFormset(forms.models.BaseInlineFormSet):
    def is_valid(self):
        return super(
            JobDescriptionInlineFormset, self).is_valid() and \
            not any([bool(e) for e in self.errors])

    def clean(self):
        job_names = set()
        for form in self.forms:
            name = form.cleaned_data['name']
            if name in job_names:
                raise forms.ValidationError(
                    "job names must be unique: " + name)

            job_names.add(name)

        dependency_tree = {}
        for form in self.forms:
            dependencies = form.cleaned_data['dependencies'].split(',')
            dependencies = [x for x in dependencies if x]
            for dependency in dependencies:
                if dependency not in job_names:
                    raise forms.ValidationError(
                        "unknown job dependency: " + dependency)

            name = form.cleaned_data['name']
            dependency_tree[name] = dependencies

        def find_circular_dependency(dependency_tree, job, path):
            if job in path:
                return path + [job]

            for dependency in dependency_tree[job]:
                cycle = find_circular_dependency(
                    dependency_tree, dependency, path + [job])
                if cycle:
                    return cycle

            return None

        for job in dependency_tree:
            cycle = find_circular_dependency(dependency_tree, job, [])
            if cycle:
                raise forms.ValidationError(
                    "circular dependency: " + ' -> '.join(cycle))


class JobDescriptionForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        exclude = []

    def clean_name(self):
        value = self.cleaned_data['name'].strip().lower()
        self.cleaned_data['name'] = value
        return value

    def clean_dependencies(self):
        value = self.cleaned_data['dependencies']
        dependencies = [x.strip().lower() for x in value.split(',')]
        dependencies = list(sorted(set(x for x in dependencies if x)))
        dependencies = ','.join(dependencies)

        self.cleaned_data['dependencies'] = dependencies
        return dependencies


class JobDescriptionInline(admin.TabularInline):
    formset = JobDescriptionInlineFormset
    model = JobDescription
    form = JobDescriptionForm
    extra = 0


class ProjectAdmin(admin.ModelAdmin):
    model = Project
    prepopulated_fields = {"slug": ("name",)}

    inlines = [
        JobDescriptionInline,
        GithubWebhookMatchInline,
        NotificationTargetInline,
    ]


class JobInline(admin.TabularInline):
    model = Job
    extra = 0


class BuildAdmin(admin.ModelAdmin):
    model = Build

    inlines = [
        JobInline,
    ]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Build, BuildAdmin)
