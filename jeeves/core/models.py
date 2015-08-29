from django.db import models


class Build(models.Model):
    class Status:
        CREATED = "created"
        RUNNING = "running"
        FINISHED = "finished"

    class Result:
        SUCCESS = "success"
        FAILURE = "failure"

    STATUS_CHOICES = [
        (Status.CREATED, Status.CREATED),
        (Status.RUNNING, Status.RUNNING),
        (Status.FINISHED, Status.FINISHED),
    ]
    RESULT_CHOICES = [
        (Result.SUCCESS, Result.SUCCESS),
        (Result.FAILURE, Result.FAILURE),
    ]

    status = models.CharField(max_length=16, choices=STATUS_CHOICES,
                              default=Status.CREATED)
    instance = models.CharField(max_length=1024)
    branch = models.CharField(max_length=1024, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    log_file = models.CharField(max_length=2048, null=True, blank=True)
    result = models.CharField(max_length=16, choices=RESULT_CHOICES,
                              null=True, blank=True)

    def get_log(self):
        return open(self.log_file).read()
