from ._md_converter import md_convert
from blog.models import Author
from django.core.management.base import BaseCommand, CommandError
import os
import time
import yaml


""" yaml file containing the description of the authors to import

The yaml file is expected to be a sequence of the following info:
* pseudo: pseudo that will be used to reference this author in the blog posts
* name:   full name as string, no format (first name last name is recommended)
* email:  valid email address format
* bio:    markdown file with the bio of the author
"""


class Command(BaseCommand):
    help = 'Replaces the authors in db with the ones referenced in the yaml '\
           'file(s)'

    def add_arguments(self, parser):
        parser.add_argument('yaml_file', nargs='+',
                            help='yaml with the list of files to import')

    def handle(self, *args, **options):
        self.profiles_nb = 0
        t = time.process_time()

        for f in options['yaml_file']:
            if not os.path.isfile(f):
                raise CommandError(f'File {f} does not exist')
            self.import_yaml(f)

        self.stdout.write(self.style.SUCCESS(
            f'Finished importing {self.profiles_nb} profiles (total duration: '
            f'{time.process_time() - t:.3f}s)'))

    def import_yaml(self, yaml_filename):
        with open(yaml_filename, 'r') as f:
            contents = yaml.load(f, Loader=yaml.FullLoader)

            Author.objects.all().delete()

            for author in contents:
                self.profiles_nb += 1

                filename = author['bio']

                if not os.path.isabs(filename):
                    base_dir = os.path.abspath(os.path.dirname(yaml_filename))
                    filename = os.path.join(base_dir, filename)

                if not os.path.isfile(filename):
                    raise CommandError(f'In file {yaml_filename}, '
                                       f'file {filename} does not exist')

                db_author = Author(pseudo=author['pseudo'],
                                   name=author['name'],
                                   email=author['email'],
                                   bio=md_convert(filename))

                db_author.save()
