import sys

from django.core.management.base import BaseCommand, CommandError
from django.utils import simplejson as json

from hyson.utils import load_obj
from hyson.ordereddict import OrderedDict


class Command(BaseCommand):
    help = 'Converts django form to ext.js xtype-based form'

    def handle(self, *args, **options):

        """
        form_module, form_name = args[0].rsplit(".", 1)

        __import__(form_module)
        module = sys.modules[form_module]

        print "Loading form '%s' from '%s'" % (form_name, module.__file__)
        form = getattr(module, form_name)
        instance = form()
        """
        
        instance = load_obj(args[0])

        form_elements = list()

        for name, field in instance.fields.items():
            print name, field.label, dir(field), dir(field.widget), field.widget.input_type
            element = {'xtype': FIELDTYPES[field.widget.input_type], 'name': name}

            if field.label:
                element['label'] = field.label

            form_elements.append(element)

        print ExtForm(items=form_elements, title='Form Fields', width=340, bodyPadding=5)
