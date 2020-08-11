from blog.models import BlogPost
from django.shortcuts import render


def index(request):
    blog_posts = BlogPost.objects.all()
    return render(request, 'blog/index.html', {'blog_posts': blog_posts})
