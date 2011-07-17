import sys

from django.core.management.base import BaseCommand, CommandError
#from django.utils import simplejson as json

from hyson.utils import load_obj
#from hyson.ordereddict import OrderedDict
from hyson.ext_component import ExtWindow, ExtGrid
from hyson.field_types import COLUMN_TYPES
from hyson.model import convert
#from django.views.generic.list import ListView

from django.forms import forms

class Command(BaseCommand):
    help = 'Converts django ListView to ext.js window with a grid'

    def _get_columns(self, instance):
        """
        Extract column names and types from model definition
        """

        columns = list()

        for field in instance._meta._fields():

            if field.name == 'id':
                continue

            #field = instance._meta.get_field_by_name(field_name)[0]

            field_class = field.__class__.__name__

            ext_type = COLUMN_TYPES[field_class]

            field_dict = {
                'text': field.verbose_name if hasattr(field, 'verbose_name') else field.name,
                'dataIndex': field.name,
                'flex': 1
            }

            if ext_type is not None:
                field_dict['xtype'] = ext_type

            if ext_type == 'date':
                field_dict['renderer'] = 'Ext.util.Format.dateRenderer(\'d.m.Y H:i\')'

            columns.append(field_dict)

        return columns

    def _get_model(self, instance):
        return instance.model

    def handle(self, *args, **options):

        view = load_obj(args[0])
        model = self._get_model(view)

        columns = self._get_columns(model)

        grid = ExtGrid(columns=columns)

        grid.params['store']['model'] = model.__name__
        grid.params['store']['proxy']['directFn'] = "%s.%s" % (view.__module__.replace(".views",""), view.__name__)
        #grid.params['title'] =

        title = model._meta.verbose_name_plural.capitalize() if hasattr(model._meta, "verbose_name_plural") else ""

        print unicode(ExtWindow(as_class=True, name=view.__name__+"Window", items=grid, title=title)).encode("utf-8") +\
            "\n\n" + unicode(convert(model)).encode("utf-8")

