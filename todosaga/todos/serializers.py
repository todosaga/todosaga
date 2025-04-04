from rest_framework import serializers
from .models import Todo

# Serializer for creating a Todo
class TodoCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    categories = serializers.ListField(
        child=serializers.CharField(), default=list, help_text="List of categories."
    )
    type = serializers.ChoiceField(choices=[(Todo.CHECK, "Check"), (Todo.TIMER, "Timer")])
    duration_seconds = serializers.IntegerField(
        required=False, help_text="Required if type is 'timer'."
    )

# Serializer for returning a Todo
class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ("id", "title", "categories", "type", "completed", "created_at")

# Serializer for Start Timer response
class StartTimerResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    start_time = serializers.DateTimeField()

# Serializer for Todo Complete response
class TodoCompleteResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    gained_exp = serializers.IntegerField()
    completed_at = serializers.DateTimeField()

# Serializer for Todo Suggestions
class TodoSuggestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    categories = serializers.ListField(child=serializers.CharField())
    reason = serializers.CharField()
