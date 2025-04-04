from django.urls import path
from .views import (
    TodoCreateView, TodoListView,
    TodoStartTimerView, TodoCompleteView,
    TodoSuggestionsView,
)

urlpatterns = [
    path('todos', TodoCreateView.as_view(), name='todo-create'),
    path('todos', TodoListView.as_view(), name='todo-list'),
    path('todos/<int:id>/start', TodoStartTimerView.as_view(), name='todo-start'),
    path('todos/<int:id>/complete', TodoCompleteView.as_view(), name='todo-complete'),
    path('todos/suggestions', TodoSuggestionsView.as_view(), name='todo-suggestions'),
]
