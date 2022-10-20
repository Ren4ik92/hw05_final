from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Follow, Likes
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from .units import paginator_posts, MESSAGE_N
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    user = request.user
    context = {
        'page_obj': paginator_posts(post_list, MESSAGE_N, request),
        'user': user
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    post_list = Post.objects.all()
    context = {
        'group': group,
        'page_obj': paginator_posts(post_list, MESSAGE_N, request)
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user_post_list = author.posts.select_related('author')
    following = (request.user.is_authenticated and (Follow.objects.filter(
        user=request.user, author=author).exists()))
    context = {
        'page_obj': paginator_posts(user_post_list, MESSAGE_N, request),
        'author': author,
        'following': following,

    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id, ):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect('posts:profile', post.author)

    return render(
        request,
        'posts/create_post.html',
        {
            'form': form,
        }
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': paginator_posts(posts, MESSAGE_N, request)
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author and Follow.objects.filter(
            user=request.user, author=author).exists():
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', author)


@login_required
def likes_post(request):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)

        if user in post_obj.liked.all():
            post_obj.liked.remove(user)
        else:
            post_obj.liked.add(user)
        like, create = Likes.objects.get_or_create(user=user, post_id=post_id)

        if not create:
            if like.value == 'Like':
                like.value = 'Unlike'
            else:
                like.value = 'Like'
        like.save()
    return redirect('posts:index')


