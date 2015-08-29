import hmac
import json
from hashlib import sha1
from multiprocessing import Process

from django.conf import settings
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, TemplateView, View

from jeeves.core.models import Build
from jeeves.core.service import handle_push_hook_request, start_build


class IndexView(TemplateView):
    template_name = "index.html"


class BuildListView(ListView):
    model = Build
    template_name = "build_list.html"

    def get_queryset(self):
        queryset = super(BuildListView, self).get_queryset()
        return queryset.order_by('-id')

    def get_context_data(self, *args, **kwargs):
        context = super(BuildListView, self).get_context_data(*args, **kwargs)
        context['last_build'] = self.get_queryset().first()
        return context


class BuildDetailView(DetailView):
    model = Build
    template_name = "build_detail.html"


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
