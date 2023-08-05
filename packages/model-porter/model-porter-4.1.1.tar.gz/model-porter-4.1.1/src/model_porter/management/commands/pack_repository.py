from django.core.management.base import BaseCommand
from model_porter.repository import create_archive_file


class Command(BaseCommand):
    help = "Package a specially-structured directory into a repository file."

    def add_arguments(self, parser):
        parser.add_argument(
            'path',
            metavar='path',
            type=str,
            nargs='?',
            help='a path to a repository directory')

    def handle(self, path, **options):

        path = create_archive_file(path)
        self.stdout.write(self.style.SUCCESS("A repository file was created at {}".format(path)))
