from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.index, name='index'),
    path('author/<int:author_id>', views.author_bio, name='author_bio'),
    path('blogpost/<int:blogpost_id>', views.blogpost, name='blogpost')
]
