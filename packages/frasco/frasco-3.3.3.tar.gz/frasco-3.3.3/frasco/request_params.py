from flask import request, abort, current_app, has_request_context
from .utils import unknown_value
from .ctx import FlagContextStack
from werkzeug.exceptions import HTTPException
from werkzeug.datastructures import MultiDict
from dateutil.parser import parse as parse_date
import functools
import inspect


try:
    from marshmallow import Schema as MarshmallowSchema, EXCLUDE as MA_EXCLUDE_UNKNOWN
    from marshmallow.fields import Field as MarshmallowField
    from marshmallow.exceptions import ValidationError as MarshmallowValidationError
    marshmallow_available = True
except ImportError:
    marshmallow_available = False


def _value_from_multidict(v, aslist=False):
    if aslist:
        return v
    if len(v) == 0:
        return None
    if len(v) == 1:
        return v[0]
    return v


class MissingRequestParam(Exception):
    pass


class RequestParamCoerceError(Exception):
    pass


def locate_request_data(location=None):
    if location is None:
        if request.is_json:
            return request.get_json(silent=True)
        return request.values
    if location == 'json':
        return request.get_json(silent=True)
    return getattr(request, location, {})


def get_request_param_value(name, location=None, aslist=False, request_data=None):
    if request_data is not None:
        if name not in request_data:
            raise MissingRequestParam()
        if isinstance(request_data, MultiDict):
            return _value_from_multidict(request_data.getlist(name), aslist)
        value = request_data[name]
        if aslist and not isinstance(value, (tuple, list)):
            value = [] if value is None else [value]
        return value

    if (not location or location == 'view_args') and name in request.view_args:
        if aslist and not isinstance(request.view_args[name], list):
            return [] if request.view_args[name] is None else [request.view_args[name]]
        return request.view_args[name]

    if not request.is_json:
        if not location or location == 'values':
            if name in request.values:
                return _value_from_multidict(request.values.getlist(name), aslist)
        elif location == 'args' and name in request.args:
            return _value_from_multidict(request.args.getlist(name), aslist)
        elif location == 'form' and name in request.form:
            return _value_from_multidict(request.form.getlist(name), aslist)

    if (not location or location == 'json') and request.is_json:
        data = request.get_json(silent=True)
        if isinstance(data, dict) and name in data:
            if aslist and not isinstance(data[name], list):
                return [] if data[name] is None else [data[name]]
            return data[name]

    if (not location or location == 'files') and name in request.files:
        return _value_from_multidict(request.files.getlist(name), aslist)

    raise MissingRequestParam()


VALUE_AS_DEST = object()


def format_marshmallow_validation_error(e):
    return "\n - " + "\n - ".join("%s: %s" % i for i in e.normalized_messages().items())


def get_marshmallow_schema(class_or_instance):
    if inspect.isclass(class_or_instance) and issubclass(class_or_instance, MarshmallowSchema):
        return class_or_instance
    if isinstance(class_or_instance, MarshmallowSchema):
        return class_or_instance.__class__
    return None


def get_marshmallow_schema_instance(class_or_instance):
    if inspect.isclass(class_or_instance) and issubclass(class_or_instance, MarshmallowSchema):
        return class_or_instance()
    if isinstance(class_or_instance, MarshmallowSchema):
        return class_or_instance
    return None


class RequestParam(object):
    def __init__(self, name, type=None, nullable=False, required=False, loader=None, validator=None,
                 dest=None, location=None, aslist=False, aslist_iter_coerce=True, aslist_iter_loader=True,
                 help=None, default=unknown_value, **loader_kwargs):
        self.name = name
        self.type = type
        self.nullable = nullable
        self.required = required
        self.loader = loader
        self.loader_kwargs = loader_kwargs
        self.validator = validator
        self.dest = dest
        self.location = location
        self.aslist = aslist
        self.aslist_iter_coerce = aslist_iter_coerce
        self.aslist_iter_loader = aslist_iter_loader
        self.help = help
        self.default = default

    @property
    def names(self):
        return self.name if isinstance(self.name, tuple) else (self.name,)

    @property
    def types(self):
        if not self.type:
            return
        return self.type if isinstance(self.type, tuple) else (self.type,)

    @property
    def names_types(self):
        names = self.names
        fallback_type = None
        types = []
        if self.type:
            types = self.types
            fallback_type = types[-1]
        return [(names[i], types[i] if i < len(types) else fallback_type) for i in range(len(names))]

    @property
    def dests(self):
        if self.dest is None:
            return self.names
        elif self.dest and not isinstance(self.dest, tuple):
            return (self.dest,)
        return self.dest

    def process(self, request_data=None):
        try:
            values = self.extract(request_data)
        except MissingRequestParam:
            if self.required and self.default is unknown_value:
                if self.required is True or self.required(request_data):
                    self._abort("required field")
            if not self.default is unknown_value:
                if not isinstance(self.name, tuple):
                    values = [self.default]
                else:
                    values = self.default
            else:
                return dict()

        values = self.load(*values)
        if not self.validate(*values):
            self._abort("invalid field")
        if len(self.dests) != len(values):
            raise Exception('Mismatch between length of dest and number of values')
        if self.dest is VALUE_AS_DEST:
            return values[0]
        return dict(zip(self.dests, values))

    def _abort(self, message, code=400):
        abort(code, "%s: %s" % (", ".join(self.names), message))

    def extract(self, request_data=None):
        values = []
        for name, type in self.names_types:
            value = get_request_param_value(name, self.location, self.aslist, request_data)
            if value is None and not self.nullable:
                raise MissingRequestParam()
            if type and value is not None:
                if self.aslist and self.aslist_iter_coerce:
                    value = [self.coerce(v, type) for v in value]
                else:
                    value = self.coerce(value, type)
            values.append(value)
        return values

    def coerce(self, value, type):
        if marshmallow_available:
            try:
                schema = get_marshmallow_schema_instance(type)
                if schema:
                    return schema.load(value)
                if isinstance(type, MarshmallowField):
                    return type.deserialize(value)
            except MarshmallowValidationError as e:
                self._abort(format_marshmallow_validation_error(e))

        try:
            if type is bool:
                if isinstance(value, str):
                    return value.lower() not in ('False', 'false', 'no', '0')
                return bool(value)
            return type(value)
        except HTTPException as e:
            self._abort(e.description, e.code)
        except:
            self._abort("invalid value")

    def load(self, *values):
        if not self.loader:
            return values
        try:
            if self.aslist and self.aslist_iter_loader:
                rv = []
                for t in zip(*values):
                    rv.append(self.loader(*t, **self.loader_kwargs))
                return (rv,)
            else:
                rv = self.loader(*values, **self.loader_kwargs)
                if not isinstance(rv, tuple):
                    return (rv,)
                return rv
        except HTTPException as e:
            self._abort(e.description, e.code)

    def validate(self, *values):
        return not self.validator or self.validator(*values)

    def update_kwargs(self, kwargs, request_data=None):
        for name in self.names:
            if name:
                kwargs.pop(name, None)
        kwargs.update(self.process(request_data))
        return kwargs


class RequestDataParam(RequestParam):
    def __init__(self, loader, dest=VALUE_AS_DEST, location=None, validator=None):
        super().__init__(None, dest=dest, loader=loader, location=location,
                         validator=validator)

    def _abort(self, message, code=400):
        abort(code, message)

    def extract(self, request_data=None):
        if request_data is None:
            request_data = locate_request_data(self.location)
        return [request_data]

    def load(self, *values):
        if self.loader and marshmallow_available:
            schema = get_marshmallow_schema_instance(self.loader)
            if schema:
                try:
                    return [schema.load(*values, unknown=MA_EXCLUDE_UNKNOWN)]
                except MarshmallowValidationError as e:
                    self._abort(format_marshmallow_validation_error(e))

        return super().load(*values)


disable_request_params = FlagContextStack()


def update_kwargs_with_request_params(kwargs, request_params, request_data=None):
    for param in request_params:
        param.update_kwargs(kwargs, request_data)
    return kwargs


def wrap_request_param_func(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if has_request_context() and not disable_request_params.top:
            update_kwargs_with_request_params(kwargs, wrapper.request_params)
        return func(*args, **kwargs)
    wrapper.request_params = []
    wrapper.wrapped_func = func
    return wrapper


def request_param(name, type=None, cls=RequestParam, append=True, **kwargs):
    def decorator(func):
        if not append or not hasattr(func, 'request_params'):
            wrapper = wrap_request_param_func(func)
        else:
            wrapper = func
        if isinstance(name, cls):
            wrapper.request_params.append(name)
        else:
            wrapper.request_params.append(cls(name, type, **kwargs))
        return wrapper
    return decorator


def partial_request_param(name=None, type=None, cls=RequestParam, **kwargs):
    def decorator(name_=None, **kw):
        return request_param(name_ or name, type, cls=cls, **dict(kwargs, **kw))
    decorator.request_param = cls(name, type, **kwargs)
    return decorator


def partial_request_param_loader(name=None, type=None, **kwargs):
    def decorator(loader_func):
        return partial_request_param(name, type, loader=loader_func, **kwargs)
    return decorator


def _dict_to_request_params(params_dict, cls=RequestParam, **param_defaults):
    params = []
    for name, kwargs in params_dict.items():
        if isinstance(kwargs, cls):
            params.append(kwargs)
            continue
        if not isinstance(kwargs, dict):
            kwargs = dict(type=kwargs)
        params.append(cls(name, **dict(param_defaults, **kwargs)))
    return params


def request_params(params, **param_defaults):
    def decorator(func):
        if callable(params) or marshmallow_available and isinstance(params, MarshmallowSchema):
            return request_param(RequestDataParam(params, **param_defaults))(func)
        for param in (_dict_to_request_params(params, **param_defaults) if isinstance(params, dict) else params):
            func = request_param(param, **param_defaults)(func)
        return func
    decorator.params = params
    return decorator


def nested(params_dict, cls=RequestParam, **kwargs):
    params = _dict_to_request_params(params_dict, cls)
    def coerce(value):
        if not isinstance(value, dict):
            abort(400, "not a hash")
        out = {}
        for param in params:
            param.update_kwargs(out, value)
        return out
    return dict(type=coerce, **kwargs) if kwargs else coerce


def list_of(type, **kwargs):
    coerce_obj = nested(type) if isinstance(type, dict) else type
    def coerce(value):
        if not isinstance(value, (list, tuple)):
            abort(400, "not a list")
        return [coerce_obj(item) for item in value]
    kwargs['aslist'] = True
    kwargs['aslist_iter_coerce'] = False
    return dict(type=coerce, **kwargs)


def utcdate(**kwargs):
    def wrapper(value):
        if not value:
            return
        dt = parse_date(value, ignoretz=True, **kwargs)
        return dt.date()
    return wrapper


def utcdatetime(**kwargs):
    def wrapper(value):
        if not value:
            return
        return parse_date(value, **kwargs)
    return wrapper


def required_if_other(other_params):
    if not isinstance(other_params, dict):
        other_params = dict([(other_params, unknown_value)])
    def required(request_data):
        for param, expected_value in other_params.items():
            try:
                value = get_request_param_value(param, request_data=request_data)
                if callable(expected_value):
                    return expected_value(value)
                return expected_value is unknown_value or value == expected_value
            except MissingRequestParam:
                pass
        return False
    return required


def one_of(*items):
    def validator(value):
        return value in items
    return validator
