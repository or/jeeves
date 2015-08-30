import hmac
import json
from hashlib import sha1
from multiprocessing import Process

from django.conf import settings
from django.http.response import HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from jeeves.core.service import handle_push_hook_request


class GithubWebhookView(View):
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(GithubWebhookView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponse("OK")

    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body.decode())

        if request.META.get('HTTP_X_GITHUB_EVENT') == "ping":
            return HttpResponse('Hi!')

        if False:
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
