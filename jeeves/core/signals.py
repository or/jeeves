import django.dispatch

build_started = django.dispatch.Signal(providing_args=['build'])
build_finished = django.dispatch.Signal(providing_args=['build'])
job_started = django.dispatch.Signal(providing_args=['job'])
job_finished = django.dispatch.Signal(providing_args=['job'])
