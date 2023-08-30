from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page


from .forms import PostForm, CommentForm
from .models import Follow, Group, Post, User
from .utils import pagination_pages, POSTS_PER_PAGE, SAVE_VALUE_IN_CACHE


@cache_page(SAVE_VALUE_IN_CACHE, key_prefix='index_page')
def index(request):
    posts = Post.objects.select_related('author', 'group')
    page_obj = pagination_pages(request, posts, POSTS_PER_PAGE)
    title = 'Последние обновления на сайте'
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
        'title': title
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author', 'group')
    page_obj = pagination_pages(request, posts, POSTS_PER_PAGE)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    count = posts.count()
    page_obj = pagination_pages(request, posts, POSTS_PER_PAGE)
    template = 'posts/profile.html'
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'count': count,
        'following': following
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    count = author.posts.count()
    template = 'posts/post_detail.html'
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'count': count,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    template = 'posts/create_post.html'
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', form.author)
    context = {
        'form': form
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post.id)
    template = 'posts/create_post.html'
    is_edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'form': form,
        'is_edit': is_edit
    }
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.id)
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post.id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = pagination_pages(request, posts, POSTS_PER_PAGE)
    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    # мы в модель Follow добавили UniqueConstrain, эта проверка еще акутальна?
    # или там ограничения, что не может быть двух одинаковых подписок?,
    # а про автор, не автор речи нет.
    # Спасибо!
    if request.user == author:
        return redirect('posts:profile', author)
    Follow.objects.get_or_create(
        user=request.user,
        author=author
    )
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=author
    ).delete()
    return redirect('posts:profile', author)
