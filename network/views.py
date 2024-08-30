from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator

from .models import User, Posts, Follow


def index(request):
    post_obj = Posts.objects.all().order_by('date').reverse()

    current_page = request.GET.get('page')
    p = Paginator(post_obj, 10)
    current_page_posts = p.get_page(current_page)

    return render(request, "network/index.html", {
        "posts": current_page_posts,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
    
def new_post(request):
    if request.method == "POST":
        post_text = request.POST["new_post"]
        post_obj = Posts(user=request.user, post=post_text)
        post_obj.save()
        return HttpResponseRedirect(reverse("index"))
    
def following(request):
    following_users = Follow.objects.filter(user=request.user).values_list('user_follower', flat=True)
    posts_from_following = Posts.objects.filter(user__in=following_users).order_by('-date')

    current_page = request.GET.get('page')
    p = Paginator(posts_from_following, 10)
    current_page_posts = p.get_page(current_page)

    return render(request, "network/following.html", {
        "posts": current_page_posts,
    })


    
def show_profile(request, username):
    user_obj = User.objects.get(username=username)
    post_obj = Posts.objects.filter(user=user_obj.id).order_by('date').reverse()
    current_page = request.GET.get('page')
    p = Paginator(post_obj, 10)
    current_page_posts = p.get_page(current_page)

    following = Follow.objects.filter(user=user_obj)
    followers = Follow.objects.filter(user_follower=user_obj)

    print(followers)
    print(following)

    isFollowing = False

    if request.user.is_authenticated:
        isFollowing = followers.filter(user=request.user).exists()

    return render(request, "network/profile.html", {
        "posts": current_page_posts,
        "username": user_obj.username,
        "following": following.count,
        "followers": followers.count,
        "isFollowing": isFollowing,
    })

def follow(request, username):
    user_obj = User.objects.get(username=username)
    follow_obj = Follow(user=request.user, user_follower=user_obj)
    follow_obj.save()

    return redirect('profile', username=username)

def unfollow(request, username):
    user_obj = User.objects.get(username=username)
    follow_obj = Follow.objects.filter(user=request.user, user_follower=user_obj).first()

    if follow_obj:
        follow_obj.delete()

    return redirect('profile', username=username)

def edit_post(request):
    if request.method == "POST":
        post_id = request.POST["post_id"]
        post_content = request.POST["edited_post"]

        post_obj = Posts.objects.get(pk=post_id)
        post_obj.post = post_content
        post_obj.save()

        print(post_obj)

        return JsonResponse({"post": post_content}, safe=False)
    
def like_post(request, pk):
    if request.user.is_authenticated:
        post_obj = Posts.objects.get(id=pk)
        if post_obj.likes.filter(id=request.user.id):
            post_obj.likes.remove(request.user)
            liked = False
        else:
            post_obj.likes.add(request.user)
            liked = True

        likes_count = post_obj.likes.count()

        response_data = {
            'likes_count': likes_count,
            'liked': liked,
        }

        return JsonResponse(response_data)
    
def likes(request):
    if not request.user.is_authenticated:
        return redirect('login')

    liked_posts = Posts.objects.filter(likes=request.user).order_by('-date')

    current_page = request.GET.get('page')
    p = Paginator(liked_posts, 10)
    current_page_posts = p.get_page(current_page)

    return render(request, "network/likes.html", {
        "posts": current_page_posts,
    })
