# -*- coding: utf-8 -*-

import sys
import re

def load_obj(module_str):
    """
    Get object class by full path

    :param module_str: Full path to object to load, for example 'app.views.View'
    """
    module_name, klass_name = module_str.rsplit(".", 1)
    __import__(module_name)

    module = sys.modules[module_name]
    #print "Loading form '%s' from '%s'" % (klass_name, module.__file__)
    klass = getattr(module, klass_name)
    return klass


FIELDTYPES = {
    'file': 'filefield',
    'hidden': 'hiddenfield'
}

#from hyson.ext_component import ExtComponent, ExtForm

def convert_form(instance):
    form_elements = list()

    for name, field in instance.fields.items():
        print name, field.label, dir(field), dir(field.widget), field.widget.input_type
        element = {'xtype': FIELDTYPES[field.widget.input_type], 'name': name}

        if field.label:
            element['label'] = field.label

        form_elements.append(element)

    return ExtForm(items=form_elements, title='Form Fields', width=340, bodyPadding=5)


def extract_form_fields(instance):
    return [name for name, field in instance.fields.items()]

def dejsonize(str):
    return re.sub('"([a-zA-Z_]*?)": ', "\g<1>: ", str)