from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox_view, name='chat_inbox'),
    path('<str:username>/', views.chat_room_view, name='chat_room'),
]