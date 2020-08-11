from ._md_converter import md_convert
from blog.models import BlogPost, Author
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import make_aware
import os
import time
import yaml


""" yaml file containing the description of the blog posts to import

The yaml file is expected to be a sequence of the following info:
* file:     filename with absolute or relative path (relative to the yaml file)
* author:   a pseudo that corresponds to a profile in the authors table
* pub_date: date of publication of the blog post (post won't be visible before)
* tags:     list of space-separated tags for the post

Example:
-
  file: test1.md
  author: profile1
  pub_date: 2020-08-08
  tags:
    - topic1
    - topic2
-
  file: test2.md
  author: profile2
  pub_date: 2020-08-07
  tags:
    - topic1
    - topic3

"""


class Command(BaseCommand):
    help = 'Imports the blog articles referenced in the yaml file(s)'

    def add_arguments(self, parser):
        parser.add_argument('yaml_file', nargs='+',
                            help='yaml with the list of files to import')

    def handle(self, *args, **options):
        self.posts_nb = 0
        t = time.process_time()

        for f in options['yaml_file']:
            if not os.path.isfile(f):
                raise CommandError(f'File {f} does not exist')
            self.import_yaml(f)

        self.stdout.write(self.style.SUCCESS(
            f'Finished importing {self.posts_nb} posts (total duration: '
            f'{time.process_time() - t:.3f}s)'))

    def import_yaml(self, yaml_filename):
        with open(yaml_filename, 'r') as f:
            contents = yaml.load(f, Loader=yaml.FullLoader)

            BlogPost.objects.all().delete()

            for blog_post in contents:
                self.posts_nb += 1
                filename = blog_post['file']

                if not os.path.isabs(filename):
                    base_dir = os.path.abspath(os.path.dirname(yaml_filename))
                    filename = os.path.join(base_dir, filename)

                if not os.path.isfile(filename):
                    raise CommandError(f'In file {yaml_filename}, '
                                       f'file {filename} does not exist')

                try:
                    author = Author.objects.get(pseudo=blog_post['author'])
                except ObjectDoesNotExist:
                    raise CommandError(f'Author {blog_post["author"]} '
                                       f'referenced in file {filename} '
                                       'does not exist in the authors table')

                # a date is always naive, so we need to convert it to datetime
                # so that make_aware can convert it to an aware object
                pub_date = blog_post['pub_date']
                pub_date = datetime(pub_date.year, pub_date.month,
                                    pub_date.day)

                md_as_html = md_convert(filename)
                soup = BeautifulSoup(md_as_html, 'html.parser')
                highest_heading = None
                for heading in range(1, 7):
                    heading_text = 'h' + str(heading)
                    if soup.find(heading_text):
                        highest_heading = heading_text
                        break

                if highest_heading is None:
                    raise CommandError(f'Blog post file {filename} '
                                       'does not contain at least one header')

                title = soup.find(highest_heading).text

                db_post = BlogPost(
                    title=title,
                    content=md_as_html,
                    author=author,
                    pub_date=make_aware(pub_date),
                    original_filename=filename)

                db_post.save()
