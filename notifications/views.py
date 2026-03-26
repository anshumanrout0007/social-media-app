from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender', 'post')[:50]
    
    # Mark all as read
    notifications.filter(is_read=False).update(is_read=True)
    
    return render(request, 'notifications/list.html', {'notifications': notifications})


@login_required
def unread_count(request):
    from django.http import JsonResponse
    count = Notification.objects.filter(
        recipient=request.user, 
        is_read=False
    ).count()
    return JsonResponse({'count': count})
