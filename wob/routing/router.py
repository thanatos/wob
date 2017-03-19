import abc as _abc

import six as _6

from ..http import errors as _errors


class Router(object):
    """Dispatches incoming requests to "endpoints" to handle them."""

    def __init__(self):
        self.routes = {}

    def add_route(self, path_rule, method_handlers):
        self.routes[path_rule] = dict(method_handlers)

    def match_request(self, request):
        for path_rule, method_handlers in _6.iteritems(self.routes):
            match = path_rule.match(request.path)
            if match is not None:
                if request.method in method_handlers:
                    endpoint = method_handlers[request.method]
                    return _RouteMatch(endpoint, match)
                else:
                    return _NoMethod(match, path_rule, method_handlers)
        return NO_PATH

    def route_request(self, request):
        match_result = self.match_request(request)
        if match_result is NO_PATH:
            raise _errors.NotFound()
        if isinstance(match_result, _NoMethod):
            raise _errors.MethodNotAllowed(
                sorted(match_result.method_handlers)
            )
        return match_result.endpoint(request, **match_result.match)


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
