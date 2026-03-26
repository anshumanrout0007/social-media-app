from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from accounts.models import User
from .models import Message


@login_required
def inbox_view(request):
    # Get all users this person has chatted with
    conversations = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).values(
        'sender', 'receiver'
    ).distinct()
    
    # Build unique conversation partners list
    partner_ids = set()
    for conv in conversations:
        if conv['sender'] != request.user.id:
            partner_ids.add(conv['sender'])
        if conv['receiver'] != request.user.id:
            partner_ids.add(conv['receiver'])
    
    partners = User.objects.filter(id__in=partner_ids)
    
    # Attach last message for each
    partners_with_last_msg = []
    for partner in partners:
        last_msg = Message.objects.filter(
            Q(sender=request.user, receiver=partner) |
            Q(sender=partner, receiver=request.user)
        ).last()
        partners_with_last_msg.append({'user': partner, 'last_message': last_msg})
    
    # Sort by most recent
    partners_with_last_msg.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else 0, 
        reverse=True
    )
    
    return render(request, 'chat/inbox.html', {'conversations': partners_with_last_msg})


@login_required
def chat_room_view(request, username):
    other_user = get_object_or_404(User, username=username)
    
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')
    
    # Mark received messages as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'chat/room.html', {
        'other_user': other_user,
        'messages': messages,
    })
