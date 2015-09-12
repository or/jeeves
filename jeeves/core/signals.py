import django.dispatch

build_start = django.dispatch.Signal(providing_args=['build'])
build_finished = django.dispatch.Signal(providing_args=['build'])

reportable_job_finished = \
    django.dispatch.Signal(providing_args=['job', 'details'])
