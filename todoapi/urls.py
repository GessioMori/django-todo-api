from django.urls import path
from todos.views import UserCreate

urlpatterns = [
    path('api/register/', UserCreate.as_view()),
]
