from django.db import models


class Todo(models.Model):
    TODO_TYPE_CHOICES = [
        ("check", "Check"),
        ("Timer", "Timer"),
    ]

    title = models.CharField(max_length=255)
    categories = models.JSONField()
    type = models.CharField(max_length=10, choices=TODO_TYPE_CHOICES)
    duration_seconds = models.IntegerField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    start_time = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    gained_exp = models.IntegerField(default=0)

    def __str__(self):
        return str(self.title)
