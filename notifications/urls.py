from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_view, name='notifications'),
    path('unread/', views.unread_count, name='unread_notifications'),
]