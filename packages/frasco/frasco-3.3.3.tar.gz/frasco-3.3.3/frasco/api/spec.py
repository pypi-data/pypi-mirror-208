from apispec import APISpec
from frasco.utils import join_url_rule, AttrDict
from frasco.request_params import RequestDataParam, get_marshmallow_schema, get_marshmallow_schema_instance
import re
import inspect


try:
    from marshmallow import Schema as MarshmallowSchema
    from marshmallow.fields import Field as MarshmallowField
    from marshmallow.exceptions import ValidationError as MarshmallowValidationError
    from apispec.ext.marshmallow import MarshmallowPlugin, resolver as ma_schema_name_resolver
    from apispec.ext.marshmallow.field_converter import DEFAULT_FIELD_MAPPING
    marshmallow_available = True
except ImportError:
    marshmallow_available = False


def build_openapi_spec(api_version, with_security_scheme=False):
    plugins = []
    if marshmallow_available:
        plugins.append(MarshmallowPlugin())

    spec = APISpec(title="API %s" % api_version.version,
                    version=api_version.version,
                    openapi_version="3.0.2",
                    plugins=plugins)

    if with_security_scheme:
        spec.components.security_scheme("api_key_bearer_token", {"type": "http", "scheme": "bearer"})
        spec.components.security_scheme("api_key_header", {"type": "apiKey", "in": "header", "name": "X-Api-Key"})
        spec.components.response("InvalidUserInput", {"description": "InvalidUserInput"})
        spec.components.response("NotAuthenticatedError", {"description": "Authentification required"})
        spec.components.response("NotAuthorizedError", {"description": "Some permissions are missing to perform this request"})

    for service in api_version.iter_services():
        paths = {}
        tag = {"name": service.name}
        if service.description:
            tag["description"] = service.description
        spec.tag(tag)
        for rule, endpoint, func, options in service.iter_endpoints():
            url = convert_url_args(join_url_rule(api_version.url_prefix, join_url_rule(service.url_prefix, rule)))
            path = paths.setdefault(url, {})
            for method in options.get('methods', ['GET']):
                op = build_spec_operation(spec, url, method, func, with_security_scheme)
                op.update({
                    'operationId': service.name + '_' + endpoint,
                    'tags': [service.name]
                })
                path[method.lower()] = op
        for path, operations in paths.items():
            spec.path(path=path, operations=operations)

    return spec


def build_spec_operation(spec, url, method, func, with_security_scheme=False):
    func_apispec = getattr(func, '__apispec__', {})

    for schema in func_apispec.get('schemas', []):
        get_schema_ref(spec, schema) # register schemas

    o = {}
    if 'description' in func_apispec:
        o['description'] = func_apispec['description']
    elif func.__doc__:
        o['description'] = func.__doc__

    if 'parameters' in func_apispec:
        o["parameters"] = func_apispec['parameters']
    elif hasattr(func, 'request_params'):
        query_params, body_params, file_params = build_spec_parameters(url, method, func.request_params)
        o["parameters"] = query_params
        request_body = build_spec_request_body_from_params(body_params, file_params)
        if request_body:
            o["requestBody"] = request_body

    if "requestBody" in func_apispec:
        o["requestBody"] = func_apispec["requestBody"]

    if "responses" in func_apispec:
        o["responses"] = func_apispec["responses"]
    else:
        o["responses"] = build_spec_responses(spec, func, with_security_scheme=with_security_scheme)

    return o


def build_spec_parameters(url, method, request_params):
    path_params = []
    search_params = []
    body_params = []
    file_params = []

    for p in reversed(request_params):
        if isinstance(p, RequestDataParam):
            if not marshmallow_available or not get_marshmallow_schema(p.loader):
                continue
            schema = get_marshmallow_schema(p.loader)
            only = None
            exclude = None
            if isinstance(p.loader, MarshmallowSchema):
                only = p.loader.only
                exclude = p.loader.exclude
            for name, field in schema._declared_fields.items():
                if only is not None and name not in only:
                    continue
                if exclude is not None and name in exclude:
                    continue
                if not field.dump_only:
                    body_params.append((name, field.required, convert_type_to_spec(field)))
            continue
        for pname in p.names:
            if p.location == 'files':
                file_params.append(pname)
            elif ("{%s}" % pname) in url:
                path_params.append(build_spec_param(pname, p, 'path'))
            elif method == 'GET':
                search_params.append(build_spec_param(pname, p))
            else:
                body_params.append((pname, p.required, convert_type_to_spec(p.type)))

    query_params = path_params + search_params
    return query_params, body_params, file_params


def build_spec_param(name, request_param, loc="query"):
    o = {"name": name,
        "schema": {"type": convert_type_to_spec(request_param.type)},
        "required": loc == "path" or bool(request_param.required),
        "in": loc}
    if request_param.help:
        o['description'] = request_param.help
    return o


def build_spec_request_body_from_params(body_params, file_params):
    request_body = {}
    if body_params:
        request_body["application/json"] = {"schema": {
            "type": "object",
            "required": [n for (n, r, t) in body_params if r],
            "properties": {n: {"type": t} for (n, r, t) in body_params}
        }}

    if file_params:
        request_body["multipart/form-data"] = {"schema": {
            "type": "object",
            "properties": {
                name: {"type": "string", "format": "binary"} \
                for name in file_params
            }
        }}

    if request_body:
        return {"content": request_body}


def build_spec_responses(spec, func, with_security_scheme=False):
    responses = {
        "default": {"description": "Unexpected error"},
        "200": {"description": "Successful response"},
        "400": {"$ref": "#/components/responses/InvalidUserInput"}
    }

    if hasattr(func, '__apispec__') and 'response' in func.__apispec__:
        responses["200"] = func.__apispec__['response']
    elif hasattr(func, '__apispec__') and 'response_content' in func.__apispec__:
        responses["200"]["content"] = func.__apispec__['response_content']
    elif hasattr(func, '__apispec__') and 'response_json' in func.__apispec__:
        responses["200"]["content"] = {"application/json": func.__apispec__['response_json']}
    else:
        content = build_spec_response_content(spec, func)
        if content:
            responses["200"]["content"] = content

    if with_security_scheme:
        responses["401"] = {"$ref": "#/components/responses/NotAuthenticatedError"}
        responses["403"] = {"$ref": "#/components/responses/NotAuthorizedError"}

    return responses


def build_spec_response_content(spec, func):
    if hasattr(func, 'marshalled_with'):
        response_spec = convert_response_to_spec(spec, func.marshalled_with, func.marshal_many)
        if response_spec:
            return {"application/json": {"schema": response_spec}}


def convert_response_to_spec(spec, response_type, many=False):
    if callable(response_type) and hasattr(response_type, '__apispec__') and 'spec' in response_type.__apispec__:
        return response_type.__apispec__['spec']

    if marshmallow_available and get_marshmallow_schema(response_type):
        schema = get_marshmallow_schema(response_type)
        return build_spec_from_marshmallow_schema(spec, schema, many)

    if isinstance(response_type, dict):
        schema = {"type": "object", "properties": {}}
        for key, value in response_type.items():
            if marshmallow_available and get_marshmallow_schema(value):
                schema["properties"][key] = build_spec_from_marshmallow_schema(spec, get_marshmallow_schema_instance(value))
            elif callable(value):
                prop = convert_response_to_spec(spec, value)
                schema["properties"][key] = prop if prop else {"type": "string"}
            else:
                schema["properties"][key] = {"type": convert_type_to_spec(value)}
        return schema


def build_spec_from_marshmallow_schema(spec, schema, many=False):
    schema_ref = get_schema_ref(spec, schema.__class__ if not inspect.isclass(schema) else schema)
    if many or isinstance(schema, MarshmallowSchema) and schema.many:
        return {"type": "array", "items": schema_ref}
    return schema_ref


def get_schema_ref(spec, schema):
    schema_name = ma_schema_name_resolver(schema)
    if schema_name not in spec.components.schemas:
        spec.components.schema(schema_name, schema=schema)
    return {"$ref": "#/components/schemas/%s" % schema_name}


_url_arg_re = re.compile(r"<([a-z]+:)?([a-z0-9_]+)>")
def convert_url_args(url):
    return _url_arg_re.sub(r"{\2}", url)


def convert_type_to_spec(type):
    if marshmallow_available and isinstance(type, MarshmallowField):
        return DEFAULT_FIELD_MAPPING.get(type.__class__, ('string', None))[0]
    if type is int:
        return "integer"
    if type is float:
        return "number"
    if type is bool:
        return "boolean"
    return "string"


def api_spec(**components):
    def decorator(func):
        func.__apispec__ = components
        return func
    return decorator
