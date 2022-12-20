from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile, Post, LikePost
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    try:
        user_profile_object = Profile.objects.get(user=user_object)
    except Profile.DoesNotExist:
        user_profile_object = None
    
    posts = Post.objects.all()
    return render(request, 'index.html', {'user_profile_object': user_profile_object, 'posts': posts})

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_posts_length = len(user_posts)

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_posts_length': user_posts_length
    }

    return render(request, 'profile.html', context)



@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')



@login_required(login_url='signin')
def likePost(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post_object = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save() 
        post_object.no_of_likes += 1
        post_object.save()
        return redirect('/')
    else:
        like_filter.delete()
        post_object.no_of_likes -= 1
        post_object.save()
        return redirect('/')


@login_required(login_url='signin')
def settings(request):
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        user_profile = None
    
    if request.method == 'POST':
        if request.FILES.get('image') == None:
            image = user_profile.profileImage
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileImage = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        # image upload and display error 
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileImage = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

            return redirect('settings')

    return render(request, 'setting.html', {'user_profile':user_profile})



def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmpass = request.POST['confirmpass']

        if password == confirmpass:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email is Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username is Taken')
                return redirect('signup')
            else:
                #create an object in user model
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a Profile object for the new user
                user_model = User.objects.get(username=username)
                user_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                user_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password Does Not Match')
            return redirect('signup')
    else:
        return render(request, 'signup.html')



def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')

        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
    else:
        return render(request, 'signin.html')



@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')