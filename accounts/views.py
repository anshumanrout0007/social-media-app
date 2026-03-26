from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import SignupForm, LoginForm, EditProfileForm
from .models import User
from posts.models import Post
from social.models import Follow


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome to Pixel, {user.username}!')
        return redirect('feed')
    
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    
    form = LoginForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect(request.GET.get('next', 'feed'))
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile_user).order_by('-created_at')
    is_following = False
    
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user, 
            following=profile_user
        ).exists()
    
    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
        'followers_count': profile_user.followers_count,
        'following_count': profile_user.following_count,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    form = EditProfileForm(
        request.POST or None, 
        request.FILES or None, 
        instance=request.user
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile', username=request.user.username)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def search_view(request):
    query = request.GET.get('q', '')
    users = []
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).exclude(id=request.user.id)[:20]
    
    return render(request, 'accounts/search.html', {
        'users': users, 
        'query': query
    })