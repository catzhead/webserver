import datetime

from blog.models import Author, BlogPost
from django.shortcuts import get_object_or_404, render


def index(request):
    blog_posts = BlogPost.objects\
        .filter(pub_date__lte=datetime.date.today())\
        .order_by('-pub_date')
    return render(request, 'blog/index.html', {'blog_posts': blog_posts})


def author_bio(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    return render(request, 'blog/author.html', {'author': author})


def blogpost(request, blogpost_id):
    blog_post = get_object_or_404(BlogPost, pk=blogpost_id)
    return render(request, 'blog/blogpost.html', {'blog_post': blog_post})
