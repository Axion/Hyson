.. image:: https://github.com/Axion/Hyson/blob/master/static/hyson.png?raw=true

Hyson(Chinese green tea) is a django application which provides various extensions for simpler Ext JS 4 integration
including Ext Direct implementation for class based views, Model and Form converters.


WARNING: This code is not production ready right now

.. contents:: :local:

Class based views and Ext Direct
--------------------------------

"Ext Direct is a platform and language agnostic technology to remote server-side methods to the client-side.
Ext Direct allows for seamless communication between the client-side of an Ext JS application and all popular server
platforms." - http://www.sencha.com/products/extjs/extdirect

In short Ext Direct provides a single entry point/url which can be used to perform any calls to yout server functions
from client's javascript, with some nice additions like request batching.

So instead of writing method and url combo you can register method with Ext Direct and call it by name as function
or use it as data provider for ext.js component.

In order to use Hyson's Ext Direct implementation you need to do following steps:

0. Clone hyson repo and put it into your python path

1. In your urls.py::

    from hyson.views import API, Router

    urlpatterns = patterns('',
        ...
        url(r'^hyson/api/', API.as_view()),
        url(r'^hyson/router/', Router.as_view()),
        ...
    )

By adding this lines you define a configuration url which will tell Ext what functions you export and a router url
which will be used to call this functions

2. In your views.py::

    from django.views.generic.edit import BaseCreateView
    from hyson.views import ExtJSONResponse, ExtResponseException

    class AddEntry(BaseCreateView, ExtDirect):
        form_class = AddEntryForm


Django CRUD class based views
-----------------------------

Hyson supports all four base django views, CreteView, DeleteView, UpdateView and ListView

Note: You can use non "Base" classes like CreateView instead of BaseCreateView but they add a little overhead
for request handling.

CreateView
----------

Adding ExtDirect class as mixin to any of your Django's CreateView classes will expose it via router to javascript,
so you can use it to handle form data, including any validation for you so any validation rules defined in
model's or form's class will be applied and any errors would be sent back to ext and displayed in form.

Additionally CreateView can be exported into visual Ext form, Hyson will export your view's form and if you user
ModelForm it will export your model as well(check model convertation part)
so basically you need to write your Django code and Hyson will turn it into working GUI in a second.


ListView
--------

In order to expose ListView you need to add ExtDirect mixin to the class definition::

    class DataList(BaseListView, ExtDirect):
        model = DataModel

and convert your ListView to javascript by running::

    ./manage.py listview_to_window your_app.views.DataList > ./static/DataList.js

or::

    ./manage.py listview_to_grid your_app.views.DataList > ./static/DataList.js

path to DataList may be different for your project and it's not required to redirect output to file, you can omit
it and check output in your terminal. listview_to_window acts exactly like listview_to_grid but will wrap grid into
modal window

By running this command you will generate a file with complete grid definition with required model definition,
columns and configured proxy. As this point you can either use this file as-is, extend it(so you wouldn't need to redo
you changes of you change yout morel or listview) or directly edit in your editor.::

    Ext.onReady(function() {
        Ext.define('DataListWindow', {
            extend: 'Ext.window.Window',
            width: "50%",
            layout: "fit",
            xtype: "window",
            modal: true,
            height: "50%",
            title: "<verbose_plural of your model>",
            items: {
                xtype: "grid",
                store: {
                    model: "DataModel",
                    proxy: {
                        directFn: ext.DataList,
                        type: "direct"
                    }
                },
                columns: [
                    {
                        text: "Name",
                        dataIndex: "name",
                        flex: 1
                    },
                    ...
                ]
            }
        });

        Ext.define('DataModel', {
            extend: "Ext.data.Model",
            fields: [
                {
                    type: "string",
                    name: "id"
                },
                {
                    type: "string",
                    name: "name"
                },
                ...
            ],
            validations: [
                {
                    field: "name",
                    type: "length",
                    max: 511
                },
                {
                    field: "name",
                    type: "presence"
                }
                ...
            ]
        });
    });



Passing additional parameters
`````````````````````````````

A common way of adding additional parameters to a grid is by creating 'beforeload' listener for store and setting
store's proxy 'extraParams' values like this::

    listeners: {
        beforeload: function(store, operation){
            store.proxy.extraParams = {
                param: value
            };
        }
    }

In order to use proxy parameters on server side(for example to perfom addition filtering of data), you need
to override get_queryset function of your class based view and use 'ext_data' property::

    class DataList(BaseListView, ExtDirect):
        model = DataModel

        def get_queryset(self):
            qs = self.model.objects.all()

            project = self.ext_data.get("param")

            if project is not None:
                qs = qs.filter(param=param)

            return qs

you can use helper method provided by ExtDirect to make things even shorter::

    class DataList(BaseListView, ExtDirect):
        model = DataModel

        def get_queryset(self):
            qs = self.model.objects.all()
            qs = self._filter_ne(qs, "param")
            return qs


Returning only required fields
``````````````````````````````

By default hyson will send every field of model in queryset if you want to pass only a set of fields you can execute
'values' call on your queryset, in this example only id and project fields will be passed::

    class DataListView(BaseListView, ExtDirect):
        model = DataModel

        def get_queryset(self):
            qs = self.model.objects.all()
            return qs.values('project', 'id')


Pagination
``````````

ExtDirect mixin will take care of pagination for you, if you provide 'paginate_by' property in your ListView class hyson
will use this value when generating js for your view and will paginate using only this amount of items, if you don't
provide paginate_by, hyson will use ranges provided by client's request.

MPTT
````

You can use ListView to generate tree if your model is registered by mptt.

Changing queryset results
'''''''''''''''''''''''''
Please keep in mind that changing queryset in get_queryset may be a bad idea if you don't do it lazily and use
pagination at the same time. In this case your modifications will be applied to EVERY element in queryset
before subsetting.::

    class DataListView(BaseListView, ExtDirect):
        model = DataModel
        painate_by = 10

        def get_queryset(self):
            qs = self.model.objects.all()

            entries = list()
            for link in qs:
                entries.append({
                    'id': link.pk,
                    'link': "http://" + link.link,
                    'size': link.internal_size
                })

            return entries

depending on the number of DataModel entries, this example may be terrible slow. This can be resolved by using two
different approaches - you can move any code that outputs data to methods of model(which is the right way of
doing things if you need to use this in many places) or define '_finalize_entry' function in your ListView class,
it will be called for every QuerySet entry before serializing.::

    class DataListView(BaseListView, ExtDirect):
        model = DataModel
        painate_by = 10

        def get_queryset(self):
            return self.model.objects.all()

        def _finalize_entry(self, link):
            return {
                'id': link.pk,
                'link': "http://" + link.link,
                'size': link.internal_size
            }


DetailView
----------

You can use DetailView to generate Ext JS DataView component, by default Hyson will provide a very simple base template
that will display every property of your Model, it's up to you to implement additional display logic.

You need to provide ID to select entry to display, by default it's ID of the model, but you can configure DetailsView
as if you would use it without Hyson to use different field.

There are lot's of ways to pass your id, but two mos common are either defining your own event listener for the store:::

    


DeleteView
----------

DeleteView doen't produce any visual components, but may be used with Ext JS components like Grids and as part of APIsde

API
---

Ext JS components like Grid allows to perform more than one CRUD actions on items, for example you may allow users to
add, delete and edit rows. In this case, instead of providing 'directFn' function of your proxy - you provide and
api.


Converting models
-----------------

Hyson provides a command to turn your model definition into Ext.js one.

For example of you have a model you can convert it using model_to_extmodel command:::

    ./manage.py model_to_extmodel your_app.models.DataModel > ./static/DataModel.js

Outputting Ext.js code from Python
----------------------------------

Hyson provides a basic number of classes to output javascript code from python, this is mostly used
internally in converters but may be usefull in some cases.::

    grid = ExtGrid()
    print grid

will output grid with default predefined parameters::

    {
        xtype: "grid",
        store: {
            proxy: {
                type: "direct"
            }
        }
    }

if you pass as_class and name params to constructor, instead of raw component data you will get full extendable class::

    grid = ExtGrid(as_class=True, name=MyGrid)
    print grid

output::

    Ext.define('MyGrid', {
        extend: 'Ext.grid.Panel',
        xtype: "grid",
        store: {
            proxy: {
                type: "direct"
            }
        }
    });

passing any other params to constructor will append them to list of outputed properties::

    grid = ExtGrid(width="90%")
    print grid

output::

    {
        xtype: "grid",
        store: {
            proxy: {
                type: "direct"
            }
        },
        width: "90%"
    }

Please note that this classes do not check provided params in any way and will output them as-as.

Charting
--------

Ext JS 4 provides powerfull charting capabilities which can be utilized in Django project by using ExtChartView class.::

    from random import random
    class BarChart(ExtChartView, ExtDirect):
        xtype = 'bar'
        series = ['data1', 'data2']

        def get_series(self):
            return [{self.series[0]: random(), self.series[1]: random()} for i in range(11)]

you can convert ExtChartView to Ext JS chart by running::

    ./manage.py chartview_to_chart your_app.views.BarChart > ./static/BarChart.js

output::

    ---


If you need to configure Chart output - you can use 'defaults' property of ExtChartView to override 'defaults' of
ExtChart created for output::

      class BarChart(ExtChartView, ExtDirect):
          defaults = {
            'animate': False
          }

          ...

output::

    ---

Generating Ext js app skeleton
------------------------------
Hyson provides manage.py command to generate base Ext js powered application::

    ./manage.py startextapp <app_name>

License
-------

Hyson is licensed under GPLv3, please contact us if you want to use it in closed source software.