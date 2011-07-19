import abc
import datetime
import time

from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import View
from django.utils import simplejson, datetime_safe

from hyson.utils import extract_form_fields

def autodiscovery():
    """

    This function was taken form 'django_cron' autodiscovery function

    Auto-discover INSTALLED_APPS views.py modules and fail silently when
    not present.
    """
    import imp
    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        # For each app, we need to look for an views.py inside that app's
        # package. We can't use os.path here -- recall that modules may be
        # imported different ways (think zip files) -- so we need to get
        # the app's __path__ and look for views.py on that path.

        # Step 1: find out the app's __path__ Import errors here will (and
        # should) bubble up, but a missing __path__ (which is legal, but weird)
        # fails silently -- apps that do weird things with __path__ might
        # need to roll their own views registration.
        try:
            app_path = __import__(app, {}, {}, [app.split('.')[-1]]).__path__
        except AttributeError:
            continue

        # Step 2: use imp.find_module to find the app's admin.py. For some
        # reason imp.find_module raises ImportError if the app can't be found
        # but doesn't actually try to import the module. So skip this app if
        # its admin.py doesn't exist
        try:
            imp.find_module('views', app_path)
        except ImportError:
            continue

        # Step 3: import the app's cron file. If this has errors we want them
        # to bubble up.
        __import__("%s.views" % app)


def has_base(klass, base):
    """
    Check if any of object's mixins are subclasses of 'base'
    """
    for base_class in klass.__bases__:
        if base_class != ExtDirect and issubclass(base_class, base):
                return True

    return False



class DjangoExtJSONEncoder(simplejson.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """

    def default(self, o):
        if isinstance(o, datetime.datetime):
            d = datetime_safe.new_datetime(o)
            return int(time.mktime(d.timetuple()))
        elif isinstance(o, datetime.date):
            d = datetime_safe.new_date(o)
            return int(time.mktime(d.timetuple()))
        elif isinstance(o, datetime.time):
            return int(time.mktime(o.timetuple()))
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(DjangoExtJSONEncoder, self).default(o)

class ExtResponseException(Exception):
    """
    Should be raised if request doesn't provide required POST/GET params or if they are wrong
    """
    pass


class ExtResponse(View):

    __metaclass__ = abc.ABCMeta

    paginate_results = True

    filters = list()

    def get(self, request):
        """
        :rtype: HttpResponse
        :return: Serialized data with coirrect content type
        """
        return HttpResponse(self._get_serialized_data(request), content_type=self._content_type)

    @abc.abstractproperty
    def _content_type(self):
        """
        Abstract property that should be overwritten by subclass providing one of the encoding formats. Equals to
        content_type to be passed in HttpResponse

        :rtype: string
        :returns: mime-type

        """
        return None

    @abc.abstractmethod
    def _serialize_data(self, data):
        """
        Abstract method that should be overwritten by subclass providing one of the encoding formats, like JSON or XML

        :param data: any object, that can be serialized. list of dicts if called from '_get_serialized_data'

        :rtype: string
        :return: serialized data object
        """
        pass

    def _process_entry(self, entry):
        """
        Abstract method that should be overwritten by actual view, it transforms provided entry into
        dict that would be serialized be _get_serialized_data

        :param entry: object to be serialized

        :rtype:  dict
        :return: dictionary representing entry fields
        """
        return entry

    @abc.abstractmethod
    def _get_queryset(self, request):
        """
        Abstract method that should be overwritten by actual view and provide base queryset
        for object listing. Paging and sorting will be provided automatically.

        :rtype: QuerySet
        :return: queryset to be serialized and passed to Ext.js
        """
        pass

    def _get_serialized_data(self, request):
        """
        Performs sorting, pagind and filtering base on user-provided queryset

        :param request: request object provided by django
        """

        try:
            entries = self._get_queryset(request)
        except ExtResponseException as e:
            response = {
                'success': False,
                'error': unicode(e)
            }

            return self._serialize_data(response)


        if self.filters:
            for filter in self.filters:
                filter_val = request.REQUEST.get(filter, None)

                if filter_val:
                    entries = entries.filter(Q(**{filter: filter_val}))

        try:
            count = entries.count()
        except TypeError:
            count = len(entries)

        if self.paginate_results:
            start = int(request.REQUEST.get("start","0"))
            stop = start + int(request.REQUEST.get("limit","100"))

            entries = entries[start:stop]


        response = {
            'success': True,
            'total': count,
            'items': [self._process_entry(entry) for entry in entries]
        }

        return self._serialize_data(response)

        

class ExtJSONResponse(ExtResponse):

    ensure_ascii = False

    def _content_type(self):
        return "application/json"

    def _serialize_data(self, data):
        return simplejson.dumps(data, ensure_ascii=self.ensure_ascii)

from django.views.generic.list import BaseListView

class Router(View):
    def get(self, request):
        pass

    def _response(self, action, method, success, errors, tid, result = None, total = None):
        """
        Construct JSON serialized response for single call
        """

        response = {
            "type":"rpc",
            "tid": tid,
            "action": action,
            "method": method
        }

        if result is not None:
            if total is not None:
                response['result'] = {'total': total, 'success': True, 'data': result}
            else:
                response['result'] = {'success': True, 'data': result}

        else:
            response['result'] = {'errors': errors, 'success': success}

        return response

    def _handle_createview(self, action, method, tid, klass, request):
        """
        Validate form, if valid - create object and return success, if not - send list of errors for every field
        """
        instance = klass()
        instance.request = request
        instance.object = None
        form_class = instance.get_form_class()
        form = instance.get_form(form_class)

        if not form.is_valid():
            errors = dict()
            for field, error in form.errors.items():
                errors[field] = "\n".join(error)

            return self._response(action, method, False, errors, tid)
        else:
            form.save()
            return self._response(action, method, True, None, tid)


    def _handle_listview(self, action, method, tid, klass, data, page, start, limit):
        instance = klass()
        instance.ext_data = data
        object_list = instance.get_queryset()
        total = None

        if isinstance(object_list, list):
            results = object_list
        else:
            results = list()
            total = object_list.count()
            page_size = instance.get_paginate_by(object_list)
            if page_size:
                # page size provided by view, use 'page' param from client
                # TODO: Use pagination from Django?
                # TODO: Handle wrong pages
                object_list = object_list[page_size*page:page_size*(page+1)]
            else:
                # use 'start' and 'limit' params from client
                object_list = object_list[start:start+limit]

            for object in object_list:
                if isinstance(object, dict):
                    fields = object
                else:
                    if hasattr(instance, '_finalize_entry'):
                        fields = instance._finalize_entry(object)
                    else:
                        fields = dict()
                        for field in object._meta._fields():
                            name = field.name
                            get_choice = 'get_%s_display' % name
                            get_id = '%s_id' %name

                            if hasattr(object, get_choice):
                                value = getattr(object, get_choice)()
                            elif hasattr(object, get_id):
                                value = getattr(object, get_id)
                            else:
                                value = getattr(object, name)

                            fields[name] = value

                results.append(fields)

        return self._response(action, method, True, None, tid, results, total)

    def _handle_chart(self, action, method, tid, klass):
        instance = klass()
        instance.request = self.request
        results = instance.get_series()
        return self._response(action, method, True, None, tid, results)

    def _do_request(self, request):
        """
        Execute single call, link to CRUD django view if registered
        """
        action = request.get("action")
        method = request.get("method")
        tid = request.get("tid")
        data = request.get('data')

        klass = ExtRegister.registered_classes[action][method]

        if has_base(klass, BaseCreateView):
            return self._handle_createview(action, method, tid, klass, request)
        elif has_base(klass, BaseListView):
            data = data[0]
            page = int(data.get('page'))
            start = int(data.get('start'))
            limit = int(data.get('limit'))
            return self._handle_listview(action, method, tid, klass, data, page, start, limit)
        elif has_base(klass, ExtChartView):
            return self._handle_chart(action, method, tid, klass)


    def _wrap_response(self, response, upload):
        response = simplejson.dumps(response, ensure_ascii=False, cls=DjangoExtJSONEncoder)
        if upload:
            return HttpResponse("<html><body><textarea>\n%s\n</textarea></body></html>" % response)
        else:
            return HttpResponse(response, content_type="text/javascript")

    def post(self, request):
        autodiscovery()

        if request.raw_post_data:
            requests = simplejson.loads(request.raw_post_data)
            upload = False
        else:
            # File upload
            requests = {
                'action': request.POST.get("extAction"),
                'method': request.POST.get("extMethod"),
                'tid': request.POST.get("extTID")
            }
            upload = request.get("extUpload") == 'true'

        if isinstance(requests, dict):
            # Got single request, it may be a submitted form or just single call to any function
            response = self._do_request(requests)
            return self._wrap_response(response, upload)
        else:
            responses = list()
            for request in requests:
                responses.append(self._do_request(request))

            return self._wrap_response(responses, False)


class API(View):
    """
    Provides list of registered modules/actions in javascript or json form for Ext.Direct
    """
    def get(self, request):

        autodiscovery()

        actions = ExtDirect.get_registered_methods()

        remoting_config =  {
            'url': '/hyson/router/',
            'type': 'remoting',
	        'actions': actions
        }

        config = """Ext.ns("Ext.app"); Ext.app.REMOTING_API = %s;""" % simplejson.dumps(remoting_config)

        return HttpResponse(config, content_type="text/javascript")

        #return HttpResponse(simplejson.dumps(config), content_type='application/json',)
        

from django.views.generic.edit import BaseCreateView


class ExtRegister(type):

    registered_classes = dict()

    def __init__(cls, name, bases, attrs):
        if not "hyson.views.ExtDirect" in str(cls):
            module = cls.__module__.replace(".views", "")

            if module not in ExtRegister.registered_classes.keys():
                ExtRegister.registered_classes[module] = dict()


            ExtRegister.registered_classes[module][cls.__name__] = cls

    def extract_fields(self, klass):
        instance = klass()
        form_class = instance.get_form_class()
        instance = form_class()
        return extract_form_fields(instance)

    def get_registered_methods(self):
        """
        Converts registered classes into extjs action list

        { "Profile" : [ { "len" : 2, "name" : "getBasicInfo" } ]

        """

        exported_methods = dict()
        for module, actions in ExtRegister.registered_classes.items():

            if module not in exported_methods.keys():
                exported_methods[module] = list()

            for action, klass in actions.items():
                if has_base(klass, BaseCreateView):
                    # This is CreateView and we will dump all form fields as function arguments
                    args = self.extract_fields(klass)
                    #exported_methods[module].append({'params': args, 'name': action, 'formHandler': True})
                    exported_methods[module].append({'len': 0, 'name': action, 'formHandler': True})
                else:
                    exported_methods[module].append({'len': 1, 'name': action})

        return exported_methods


class ExtDirect(object):
    __metaclass__ = ExtRegister

    def _filter_ne(self, qs, param):
        val = self.ext_data.get(param)

        if val is not None:
            qs = qs.filter(**{'%s__%s' % (param, 'exact'): val})

        return qs


class ExtChartView(object):
    pass