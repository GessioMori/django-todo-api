from django.urls import path
from rest_framework.authtoken import views
from todos.views import Logout, TodoDetail, TodoList, UserCreate

urlpatterns = [
    path('api/register/', UserCreate.as_view()),
    path('api/login/', views.obtain_auth_token),
    path('api/logout/', Logout.as_view()),
    path('api/todos/', TodoList.as_view()),
    path('api/todos/<int:pk>/', TodoDetail.as_view()),
]
