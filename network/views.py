from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from .models import User, Post, Follow, Like
from .forms import PostForm
from django.shortcuts import render, redirect, get_object_or_404

def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)
    all_likes = Like.objects.all()
    quien_te_gusto = []
    like_counts = {}

    # Poblamos quien_te_gusto y like_counts
    for like in all_likes:
        if like.user == request.user:
            quien_te_gusto.append(like.post.id)
        if like.post.id in like_counts:
            like_counts[like.post.id] += 1
        else:
            like_counts[like.post.id] = 1

    # Asegúrate de que todos los posts tengan una entrada en like_counts
    for post in posts:
        if post.id not in like_counts:
            like_counts[post.id] = 0

    return render(request, "network/index.html", {
        "posts_of_the_page": posts_of_the_page,
        "quien_te_gusto": quien_te_gusto,
        "like_counts": like_counts,
    })

def add_like(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        like.like = True
        like.save()
        like_count = Like.objects.filter(post=post, like=True).count()
        return JsonResponse({"message": "Like added", "post_id": post_id, "liked": True, "like_count": like_count})

def remove_like(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        like = Like.objects.filter(user=request.user, post=post).first()
        if like:
            like.delete()
        like_count = Like.objects.filter(post=post, like=True).count()
        return JsonResponse({"message": "Like removed", "post_id": post_id, "liked": False, "like_count": like_count})

def newPost(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = PostForm()
    return render(request, "network/index.html", {
        "form": form
    })

def actualizar_publicacion(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        new_content = request.POST.get('new_content')
        user_id = request.user.id

        post = get_object_or_404(Post, id=post_id)
        if post.user.id == user_id:
            post.content = new_content
            post.save()
            return JsonResponse({'status': 'success', 'message': 'Post updated successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to edit this post'}, status=403)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    allPosts = Post.objects.filter(user=user).order_by("id").reverse()
    


    if request.user == user:
        siguiendo = Follow.objects.filter(user=request.user)
    
    else:
        siguiendo = Follow.objects.filter(user=user)

    seguidores = Follow.objects.filter(user_follower=user)


    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(user_follower=user)
    
    siguiendo = len(siguiendo)
    seguidores = len(seguidores)

    print(f" ====> siguiendo {siguiendo}")
    print(f" ====> seguidores {seguidores}")

    Isfollowing = None

    try:
        Isfollowing = Follow.objects.get(user=request.user, user_follower=user)
    
    except Follow.DoesNotExist:
        Isfollowing = None
    
    paginator = Paginator(allPosts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)
    
    return render(request, "network/profile.html", {
        "allPosts": allPosts,
        "posts_of_the_page": posts_of_the_page,
        "username": user.username,
        "following": following,
        "followers": followers,
        "isFollowing": Isfollowing,
        "user_profile": user
    })
        
def following(request):
    currentUser = User.objects.get(pk=request.user.id)
    followingPeople = Follow.objects.filter(user=currentUser)
    allPosts = Post.objects.all().order_by('id').reverse()
    followingPosts = []
    for post in allPosts:
        for person in followingPeople:
            if person.user_follower == post.user:
                followingPosts.append(post)
                
    paginator = Paginator(followingPosts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)
    
    return render(request, "network/Following.html", {
        "posts_of_the_page": posts_of_the_page
    })
        
def follow(request):
    userFollow = request.POST.get('userFollow')
    currentUser = User.objects.get(pk=request.user.id)
    userFollowDate = User.objects.get(username=userFollow)
    M = Follow(user=currentUser, user_follower=userFollowDate)
    M.save()
    user_id = userFollowDate.id
    return HttpResponseRedirect(reverse('profile', kwargs={'user_id': user_id}))

def unfollow(request):
    userFollow = request.POST.get('userFollow')
    currentUser = User.objects.get(pk=request.user.id)
    userFollowDate = User.objects.get(username=userFollow)
    M = Follow.objects.get(user=currentUser, user_follower=userFollowDate)
    M.delete()
    user_id = userFollowDate.id
    return HttpResponseRedirect(reverse('profile', kwargs={'user_id': user_id}))

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
    