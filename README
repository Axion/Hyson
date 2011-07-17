About
=====

![logo](https://github.com/.../static/hyson.png)

Hyson(Chinese green tea) is a django application which provides various extensions for simplier Ext.js integration
including Ext Direct implementation for class based views, Model and Form converters.


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

1. In your urls.py

    from hyson.views import API, Router

    urlpatterns = patterns('',
        ...
        url(r'^hyson/api/', API.as_view()),
        url(r'^hyson/router/', Router.as_view()),
        ...
    )

By adding this lines you define a configuration url which will tell Ext what functions you export and a router url
which will be used to call this functions

2. In your views.py

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


Converting models
-----------------

Hyson provides a command to turn your model definition into Ext.js one.

For example of you have a model like:


License
-------

Hyson is licensed under GPLv3, please contact us if you want to use it in closed source software.