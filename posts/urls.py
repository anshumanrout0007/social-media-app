from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('post/create/', views.create_post_view, name='create_post'),
    path('post/<int:post_id>/delete/', views.delete_post_view, name='delete_post'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/save/', views.toggle_save, name='toggle_save'),
    path('saved/', views.saved_posts_view, name='saved_posts'),
    path('explore/', views.explore_view, name='explore'),
]