from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from .units import paginator_posts, MESSAGE_N


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all().order_by('-pub_date')
    context = {
        'page_obj': paginator_posts(post_list, MESSAGE_N, request),
        'post_list': post_list,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    post_list = Post.objects.filter(group=group).order_by('-pub_date')
    context = {
        'group': group,
        'page_obj': paginator_posts(post_list, MESSAGE_N, request)
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user_post_list = author.posts.select_related('author').order_by(
        '-pub_date')
    context = {
        'page_obj': paginator_posts(user_post_list, MESSAGE_N, request),
        'author': author

    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id, ):
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'comments': comments,
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
