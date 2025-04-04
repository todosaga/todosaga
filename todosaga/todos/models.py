from django.db import models
from django.utils import timezone

class Todo(models.Model):
    # Todo types
    CHECK = "check"
    TIMER = "timer"
    TODO_TYPE_CHOICES = [
        (CHECK, "Check"),
        (TIMER, "Timer"),
    ]
    
    title = models.CharField(max_length=255)
    # Storing categories as a JSON list; PostgreSQL’s JSONField is used here
    categories = models.JSONField()
    type = models.CharField(max_length=10, choices=TODO_TYPE_CHOICES)
    # For timer-type todos, store the duration in seconds
    duration_seconds = models.IntegerField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Timer-specific fields
    start_time = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    gained_exp = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title
