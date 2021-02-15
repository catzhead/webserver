from django.db import models


class Author(models.Model):
    pseudo = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    bio = models.TextField()
    header_img = models.CharField(max_length=200,
                                  default='default-header-bg.jpg')


class BlogPost(models.Model):
    pub_date = models.DateTimeField('date published')
    original_filename = models.CharField(max_length=4096)
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=400)
    header_img = models.CharField(max_length=200,
                                  default='default-header-bg.jpg')
