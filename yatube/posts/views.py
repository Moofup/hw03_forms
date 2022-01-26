from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .models import Group, Post, User
from .forms import PostForm

MAX_POST_DISPLAYED = 10


def index(request):
    title = 'Последние обновления на сайте'
    template = 'posts/index.html'
    post_list = Post.objects.select_related(
        'author',
        'group'
    )
    paginator = Paginator(post_list, MAX_POST_DISPLAYED)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': title,
    }

    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    title = f'Записи сообщества {group.title}'
    template = 'posts/group_list.html'
    post_list = group.posts.all()
    paginator = Paginator(post_list, MAX_POST_DISPLAYED)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, template, context)


def profile(request, username):
    author_name = get_object_or_404(User, username=username)
    title = f'Все посты пользователя {author_name.username}'
    post_list = author_name.posts.all()
    template = 'posts/profile.html'
    paginator = Paginator(post_list, MAX_POST_DISPLAYED)
    number_of_posts = paginator.count
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author_name,
        'page_obj': page_obj,
        'title': title,
        'number_of_posts': number_of_posts,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    full_post = get_object_or_404(Post, pk=post_id)
    title = full_post.text
    author_posts = Post.objects.filter(author=full_post.author)
    number_of_posts = author_posts.count()
    template = 'posts/post_detail.html'
    context = {
        'title': title,
        'post': full_post,
        'number_of_posts': number_of_posts,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.save()
            return redirect('posts:profile', form.author)
    form = PostForm()
    template = 'posts/create_post.html'
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST, instance=post)
    template = 'posts/create_post.html'
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post.pk)
    is_edit = True
    context = {'form': form, 'is_edit': is_edit}
    return render(request, template, context)

