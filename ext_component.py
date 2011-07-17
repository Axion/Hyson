import re

from django.utils import simplejson as json

from hyson.ordereddict import OrderedDict
from hyson.utils import dejsonize

def ident(str, spacer = "    "):
    text = ""
    for i in str.split("\n"):
        text += spacer + i + "\n"

    return text

class ExtComponentEncoder(json.JSONEncoder):
    def default(self, obj):
        if issubclass(obj.__class__, ExtComponent):
            return obj.params
        return json.JSONEncoder.default(self, obj)


class ExtComponent(object):
    class_name = "Ext.Component"
    defaults = {
        'layout': 'fit'
    }

    items = None

    def __init__(self, as_class=False, name="", **kwargs):
        """
        Inits component params as OrderedDict and make sure that items list will allways be outputed last
        for better readability of json

        :param kwargs: Dict of extjs component attributes
        """

        self.as_class = as_class
        self.name = name

        self.params = OrderedDict()
        self.items = kwargs.get("items")

        if self.items:
            del kwargs["items"]

        self.params.update(self.defaults)
        self.params.update(kwargs)

        if self.items:
            self.params["items"] = self.items

    def __str__(self):

        encoder = ExtComponentEncoder(ensure_ascii=False, indent=" " * 4)
        # 'DeJSONize' output by removing " around array keys
        str = dejsonize(encoder.encode(self.params))

        if self.as_class:
            return "Ext.define('%s', {\n    extend: '%s',%s});" % (self.name, self.class_name, str.strip("{}"))
        else:
            return str


class ExtForm(ExtComponent):

    defaults = {
        'xtype': 'form',
        'frame': True,
        'fieldDefaults': {
            'labelAlign': 'left',
            'labelWidth': 90,
            'anchor': '100%'
        },
        'buttons': [{
            'text': 'Save'
        },{
            'text': 'Cancel'
        }]
    }


class ExtWindow(ExtComponent):
    class_name = "Ext.window.Window"
    defaults = {
        'xtype': 'window',
        'modal': True,
        'layout': 'fit',
        'width': '50%',
        'height': '50%'
    }

class ExtGrid(ExtComponent):

    defaults = {
        'xtype': 'grid',
        'store': {
            'proxy': {
                'type': 'direct'
            }
        },
    }