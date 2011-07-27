import sys

from django.core.context_processors import request
from django.core.management.base import BaseCommand, CommandError
from django.forms import forms

from hyson.utils import load_obj
from hyson.ext_component import ExtWindow, DataView
from hyson.field_types import COLUMN_TYPES
from hyson.model import convert


class Command(BaseCommand):
    help = 'Converts django DetailView to ext.js window with a DataView'

    def _create_template(self, klass):
        tpl = ''

        for field in klass._meta._fields():
            tpl += '<div class="thumb-wrap" id="%s">%s:{%s}</div>' % (field.name, field.name, field.name)

        return tpl

    def handle(self, *args, **options):
        view = load_obj(args[0])
        model = view.model
        tpl = self._create_template(model)

        dataview = DataView(tpl=tpl)
        title = ""

        dataview.params['store']['model'] = model.__name__
        dataview.params['store']['proxy']['directFn'] = "%s.%s" % (view.__module__.replace(".views",""), view.__name__)

        print (
            unicode(ExtWindow(as_class=True, name=view.__name__+"Window", items=dataview, title=title)) +
            "\n\n" +
            unicode(convert(model))
        ).encode("utf-8")
