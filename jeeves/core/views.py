import json

from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View, ListView, DetailView

from jeeves.core.models import Build
from jeeves.core.service import start_build


class IndexView(TemplateView):
    template_name = "index.html"


class BuildListView(ListView):
    model = Build
    template_name = "build_list.html"


class BuildDetailView(DetailView):
    model = Build
    template_name = "build_detail.html"


class GithubWebhookView(View):
    def get(self, request):
        start_build("test")
        return HttpResponse("OK")

    def post(self, request):

        return HttpResponse("oink")
