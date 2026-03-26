from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.models import User
from .models import Follow
from notifications.models import Notification


@login_required
def toggle_follow(request, username):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    target_user = get_object_or_404(User, username=username)
    
    if target_user == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target_user
    )
    
    if not created:
        follow.delete()
        following = False
    else:
        following = True
        Notification.objects.create(
            recipient=target_user,
            sender=request.user,
            notification_type='follow',
        )
    
    return JsonResponse({
        'following': following,
        'followers_count': target_user.followers_count,
    })