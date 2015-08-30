import django.dispatch

build_start = django.dispatch.Signal(providing_args=['build', 'metadata'])
build_finished = django.dispatch.Signal(providing_args=['build', 'metadata'])
