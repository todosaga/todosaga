from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Todo
from .serializers import (
    TodoCreateSerializer,
    TodoSerializer,
    StartTimerResponseSerializer,
    TodoCompleteResponseSerializer,
    TodoSuggestionSerializer,
)
from .services.todo_services import get_todo_recommendations

class TodoCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=TodoCreateSerializer,
        responses={201: TodoSerializer, 400: "Bad Request"}
    )
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
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'completed',
                openapi.IN_QUERY,
                description="Filter by completion status (true/false)",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'categories',
                openapi.IN_QUERY,
                description="Filter by categories (can be provided multiple times)",
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING)
            )
        ],
        responses={200: TodoSerializer(many=True)}
    )
    def get(self, request):
        completed_param = request.query_params.get("completed")
        categories = request.query_params.getlist("categories")
        todos = Todo.objects.all()
        
        if completed_param is not None:
            if completed_param.lower() == "true":
                todos = todos.filter(completed=True)
            elif completed_param.lower() == "false":
                todos = todos.filter(completed=False)
        
        if categories:
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
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={200: StartTimerResponseSerializer, 400: "Bad Request"}
    )
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
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={200: TodoCompleteResponseSerializer, 400: "Bad Request"}
    )
    def post(self, request, id):
        todo = get_object_or_404(Todo, id=id)
        if todo.completed:
            return Response({"detail": "Todo already completed."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        todo.completed = True
        todo.completed_at = timezone.now()
        todo.gained_exp = 10  # Adjust your experience calculation logic as needed.
        todo.save()
        result = {
            "message": "Todo completed",
            "gained_exp": todo.gained_exp,
            "completed_at": todo.completed_at,
        }
        return Response(result, status=status.HTTP_200_OK)

class TodoSuggestionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={200: TodoSuggestionSerializer(many=True)}
    )
    def get(self, request):
        user_todos = Todo.objects.filter(user=request.user).order_by('-created_at')[:10]
        if user_todos.exists():
            todo_list_str = "\n".join([f"- {todo.title}" for todo in user_todos])
        else:
            # Fallback default TODO list
            todo_list_str = (
                "- 아침 루틴 정립하기 (기상 시간, 스트레칭, 물 마시기 등)\n"
                "- 주간 회의 안건 정리 및 공유\n"
                "- 'Effective Python' 1~3장 읽고 요약 정리하기\n"
                "- 냉장고 정리 및 유통기한 지난 식재료 폐기\n"
                "- 30분간 걷기 운동 후 심박수 기록하기\n"
                "- 후쿠오카 여행 일정 Google Calendar에 정리하기\n"
                "- 3월 생활비 지출 내역 가계부에 입력하기\n"
                "- Django 서버에 OAuth 로그인 기능 통합 테스트\n"
                "- ChatGPT를 활용한 단편 시나리오 1편 초안 작성\n"
                "- 책상 위 케이블 정리하고 선정리함 설치"
            )
        # Call the recommendation service to generate suggestions based on the TODO list.
        recommendations = get_todo_recommendations(todo_list_str)
        return Response(recommendations, status=status.HTTP_200_OK)
