import django.dispatch

build_start = django.dispatch.Signal(providing_args=['build'])
build_finished = django.dispatch.Signal(providing_args=['build'])
