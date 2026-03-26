from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Post, Like, Comment, SavedPost
from .forms import PostForm, CommentForm
from social.models import Follow
from notifications.models import Notification


@login_required
def feed_view(request):
    # Get users that request.user follows
    following_users = Follow.objects.filter(
        follower=request.user
    ).values_list('following', flat=True)
    
    posts = Post.objects.filter(
        author__in=following_users
    ).select_related('author').prefetch_related('likes', 'comments')
    
    # Add own posts to feed
    own_posts = Post.objects.filter(author=request.user)
    feed = (posts | own_posts).distinct().order_by('-created_at')
    
    paginator = Paginator(feed, 10)
    page = request.GET.get('page', 1)
    posts_page = paginator.get_page(page)
    
    # Get liked posts by user for UI state
    liked_posts = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    saved_posts = SavedPost.objects.filter(user=request.user).values_list('post_id', flat=True)
    
    context = {
        'posts': posts_page,
        'liked_posts': liked_posts,
        'saved_posts': saved_posts,
        'comment_form': CommentForm(),
    }
    return render(request, 'posts/feed.html', context)


@login_required
def create_post_view(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, 'Post shared successfully!')
        return redirect('feed')
    
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def delete_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('feed')
    return render(request, 'posts/confirm_delete.html', {'post': post})


@login_required
def toggle_like(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        # Create notification (not for own posts)
        if post.author != request.user:
            Notification.objects.get_or_create(
                recipient=post.author,
                sender=request.user,
                notification_type='like',
                post=post
            )
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes_count
    })


@login_required
def add_comment(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.post = post
        comment.save()
        
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type='comment',
                post=post
            )
        
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'text': comment.text,
                'username': comment.user.username,
                'profile_pic': comment.user.profile_pic.url if comment.user.profile_pic else '',
                'created_at': comment.created_at.strftime('%b %d'),
            },
            'comments_count': post.comments_count,
        })
    
    return JsonResponse({'error': 'Invalid comment'}, status=400)


@login_required
def toggle_save(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    post = get_object_or_404(Post, id=post_id)
    save, created = SavedPost.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        save.delete()
        saved = False
    else:
        saved = True
    
    return JsonResponse({'saved': saved})


@login_required
def saved_posts_view(request):
    saved = SavedPost.objects.filter(
        user=request.user
    ).select_related('post__author').order_by('-created_at')
    
    liked_posts = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    saved_ids = saved.values_list('post_id', flat=True)
    
    return render(request, 'posts/saved.html', {
        'saved_posts': saved,
        'liked_posts': liked_posts,
        'saved_post_ids': saved_ids,
    })


@login_required
def explore_view(request):
    # Random posts excluding own
    posts = Post.objects.exclude(
        author=request.user
    ).select_related('author').order_by('?')[:30]
    
    liked_posts = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    saved_posts = SavedPost.objects.filter(user=request.user).values_list('post_id', flat=True)
    
    return render(request, 'posts/explore.html', {
        'posts': posts,
        'liked_posts': liked_posts,
        'saved_posts': saved_posts,
    })