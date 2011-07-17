import sys

from django.core.management.base import BaseCommand, CommandError

from hyson.utils import load_obj
from hyson.field_types import FIELD_TYPES
from hyson.model import convert

class Command(BaseCommand):
    help = 'Converts django model to ext.js model'

    def handle(self, *args, **options):
        instance = load_obj(args[0])
        print convert(instance)
