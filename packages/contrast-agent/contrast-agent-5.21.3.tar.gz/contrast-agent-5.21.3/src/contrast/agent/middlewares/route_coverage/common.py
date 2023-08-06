# -*- coding: utf-8 -*-
# Copyright © 2023 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
Rules for coverage:

- new routes on init get count 0
- new routes after init get count 1 per context
- routes without a method type specified on init are ['GET', 'POST']
- a route needs verb, route, url, and count
- url should be normalized uri
- route should be the path to the view function (aka controller for Java people)
- one method type per route

Example:
      GET /blog/foo/bar - app.blogs.find(request, ) 0
"""

import re


DEFAULT_ROUTE_METHODS = ("GET", "POST")

# 1 or more digits, then a group: either '/' or end of string
DIGITS_ONLY_PATH_COMPONENT = r"/\d+(/|$)"

# Retruns digits between '/' or end of string
FIND_REQEUST_PARAMS = r"(?<=\/)\d+(?=\/|$)"


def get_normalized_uri(path):
    """
    A best-effort to remove client-specific information from the path.

    Example:
    /user/123456/page/12 -> /user/{n}/page/{n}
    """
    return re.sub(DIGITS_ONLY_PATH_COMPONENT, r"/{n}\1", path)


def get_url_parameters(path):
    """
    A best-effort to remove client-specific information from the path.

    Example:
    /user/123456/page/12 -> /user/{n}/page/{n}
    """
    return re.findall(FIND_REQEUST_PARAMS, path)


def build_route(view_func_name, view_func):
    view_func_args = build_args_from_function(view_func)
    return view_func_name + view_func_args


def build_key(route_id, method):
    return "_".join([route_id, method])


def build_args_from_function(func):
    """
    Attempts to grab argument names from the function definition.

    Defaults to () if none exist
    If there is no view function, like in the case of a pure WSGI app, then the func will
    be a string like '/sqli' and we just return that.

    """
    method_arg_names = "()"
    if func is not None and hasattr(func, "__code__"):
        method_arg_names = str(
            func.__code__.co_varnames[0 : func.__code__.co_argcount]
        ).replace("'", "")
    elif isinstance(func, str):
        method_arg_names = func

    return method_arg_names
