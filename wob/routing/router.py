import abc as _abc

import six as _6

from ..http import errors as _errors


NO_PATH = object()


class _NoMethod(object):
    def __init__(self, match, path_rule, method_handlers):
        self.match = match
        self.path_rule = path_rule
        self.method_handlers = method_handlers


class _RouteMatch(object):
    def __init__(self, endpoint, match):
        self.endpoint = endpoint
        self.match = match


class Router(object):
    def __init__(self):
        self.routes = {}

    def add_route(self, path_rule, method_handlers):
        self.routes[path_rule] = dict(method_handlers)

    def match_request(self, request):
        for path_rule, method_handlers in _6.iteritems(self.routes):
            match = path_rule.match(request.path)
            if match is not None:
                request_method = request.method.upper()
                for methods, endpoint in _6.iteritems(method_handlers):
                    if methods.matches(request_method):
                        return _RouteMatch(endpoint, match)
                return _NoMethod(match, path_rule, method_handlers)
        return NO_PATH

    def route_request(self, request):
        match_result = self.match_request(request)
        if match_result is NO_PATH:
            raise _errors.NotFound()
        if isinstance(match_result, _NoMethod):
            allow = set()
            for methods in match_result.method_handlers:
                allow |= methods.methods
            raise _errors.MethodNotAllowed(allow)
        return match_result.endpoint(request, match_result.match)


class Methods(object):
    def __init__(self, *args):
        self.methods = frozenset(arg.upper() for arg in args)

    def matches(self, method):
        """Test if a method matches this Methods object.

        ``method`` MUST be uppercased prior to calling this function.
        """
        return method in self.methods


GET = Methods('GET')
PUT = Methods('PUT')
DELETE = Methods('DELETE')
POST = Methods('POST')
