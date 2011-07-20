import sys

from django.core.management.base import BaseCommand, CommandError
#from django.utils import simplejson as json

from hyson.utils import load_obj
#from hyson.ordereddict import OrderedDict
from hyson.ext_component import ExtWindow, ExtChart
from hyson.field_types import COLUMN_TYPES
from hyson.model import convert
#from django.views.generic.list import ListView

from django.forms import forms

class Command(BaseCommand):
    help = 'Converts ExtChartView to ext.js chart'

    def handle(self, *args, **options):
        view = load_obj(args[0])

        chart = ExtChart()
        window = ExtWindow(as_class=True, name=view.__name__+"Window", items=chart)

        print window