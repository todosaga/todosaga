from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Todo

class TodoCreateView(APIView):
    """
    POST /todos
    Creates a new Todo.
    Expected JSON:
    {
        "title": "Study Python",
        "categories": ["study", "programming"],
        "type": "check",       // or "timer"
        "duration_seconds": 1800  // required if type is "timer"
    }
    """
    def post(self, request):
        data = request.data
        title = data.get("title")
        categories = data.get("categories", [])
        todo_type = data.get("type")
        duration_seconds = data.get("duration_seconds")
        
        if not title or not todo_type:
            return Response({"detail": "Title and type are required."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if todo_type == Todo.TIMER and duration_seconds is None:
            return Response({"detail": "duration_seconds is required for timer type."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        todo = Todo.objects.create(
            title=title,
            categories=categories,
            type=todo_type,
            duration_seconds=duration_seconds
        )
        result = {
            "id": todo.id,
            "title": todo.title,
            "categories": todo.categories,
            "type": todo.type,
            "completed": todo.completed,
            "created_at": todo.created_at,
        }
        return Response(result, status=status.HTTP_201_CREATED)

class TodoListView(APIView):
    """
    GET /todos
    Retrieves a list of Todos. Optionally filter by:
      - completed (query parameter, boolean)
      - categories (query parameter, array of strings)
    """
    def get(self, request):
        completed_param = request.query_params.get("completed")
        categories = request.query_params.getlist("categories")
        todos = Todo.objects.all()
        
        if completed_param is not None:
            # Convert string to boolean
            if completed_param.lower() == "true":
                todos = todos.filter(completed=True)
            elif completed_param.lower() == "false":
                todos = todos.filter(completed=False)
        
        if categories:
            # Assuming categories is stored as a list in JSONField,
            # and using PostgreSQL we can filter using __contains or __overlap.
            todos = todos.filter(categories__overlap=categories)
        
        result = []
        for todo in todos:
            result.append({
                "id": todo.id,
                "title": todo.title,
                "categories": todo.categories,
                "type": todo.type,
                "completed": todo.completed,
                "created_at": todo.created_at,
            })
        return Response(result, status=status.HTTP_200_OK)

class TodoStartTimerView(APIView):
    """
    POST /todos/{id}/start
    Starts the timer for a timer-type Todo.
    """
    def post(self, request, id):
        todo = get_object_or_404(Todo, id=id)
        if todo.type != Todo.TIMER:
            return Response({"detail": "Only timer type todos can be started."},
                            status=status.HTTP_400_BAD_REQUEST)
        if todo.start_time is not None:
            return Response({"detail": "Timer already started."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        todo.start_time = timezone.now()
        todo.save()
        result = {
            "message": "Timer started",
            "start_time": todo.start_time,
        }
        return Response(result, status=status.HTTP_200_OK)

class TodoCompleteView(APIView):
    """
    POST /todos/{id}/complete
    Marks a Todo as complete.
    """
    def post(self, request, id):
        todo = get_object_or_404(Todo, id=id)
        if todo.completed:
            return Response({"detail": "Todo already completed."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        todo.completed = True
        todo.completed_at = timezone.now()
        # Here we set gained_exp; you can adjust the logic as needed.
        todo.gained_exp = 10
        todo.save()
        result = {
            "message": "Todo completed",
            "gained_exp": todo.gained_exp,
            "completed_at": todo.completed_at,
        }
        return Response(result, status=status.HTTP_200_OK)

class TodoSuggestionsView(APIView):
    """
    GET /todos/suggestions
    Returns customized Todo suggestions.
    For demonstration purposes, this example returns static suggestions.
    In a real application, you might generate these based on user data.
    """
    def get(self, request):
        suggestions = [
            {
                "id": 201,
                "title": "Clean room",
                "categories": ["cleaning", "home"],
                "reason": "Based on your preference for organized tasks."
            },
            {
                "id": 202,
                "title": "Grocery shopping",
                "categories": ["shopping", "home"],
                "reason": "To restock your kitchen supplies."
            },
            {
                "id": 203,
                "title": "Evening walk",
                "categories": ["health", "wellbeing"],
                "reason": "Helps to relax and improve health."
            }
        ]
        return Response(suggestions, status=status.HTTP_200_OK)
