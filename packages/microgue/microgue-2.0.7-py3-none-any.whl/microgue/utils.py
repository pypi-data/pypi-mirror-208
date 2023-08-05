import json
from flask import Response, request, g


def set_authenticated(authenticated=True):
    g.authenticated = authenticated


def get_request_method():
    return request.method


def get_request_headers(key=None, default=""):
    if key:
        if request.headers:
            return request.headers.get(key, default)
        else:
            return default
    else:
        if request.headers:
            return dict(request.headers)
        else:
            if default != "":
                return default
            else:
                return {}


def get_request_data(key=None, default=""):
    if key:
        if request.data:
            return json.loads(request.data).get(key, default)
        else:
            return default
    else:
        if request.data:
            return json.loads(request.data)
        else:
            if default != "":
                return default
            else:
                return {}


def get_request_form(key=None, default=None):
    # defaults
    default = [] if default is None else default

    if key:
        if request.form:
            return request.form.getlist(key)
        else:
            return default
    else:
        if request.form:
            form = {}
            keys = request.form.keys()
            for key in keys:
                form[key] = request.form.getlist(key)
            return form
        else:
            if default != []:
                return default
            else:
                return {}


def get_request_files(key=None, default=""):
    if key:
        if request.files:
            return request.files.get(key, default)
        else:
            return default
    else:
        if request.files:
            return dict(request.files)
        else:
            if default != "":
                return default
            else:
                return {}


def get_request_args(key=None, default=""):
    if key:
        if request.args:
            return request.args.get(key, default)
        else:
            return default
    else:
        if request.args:
            return dict(request.args)
        else:
            if default != "":
                return default
            else:
                return {}


def get_request_url():
    return request.url


def mask_fields_in_data(data, fields, mask="*****"):
    data = data.copy()
    for field in fields:
        if field in data:
            data[field] = mask
    return data


class JSONResponse(Response):
    default_mimetype = "application/json"

    def __init__(self, data, *args, **kwargs):
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data)
        super().__init__(data, *args, **kwargs)
