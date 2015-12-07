import abc as _abc

import six as _6

from ..http import response as _response


NO_PATH = object()
NO_METHOD = object()


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
                for method, endpoint in _6.iteritems(method_handlers):
                    if method.matches(request_method):
                        return endpoint, match
                return NO_METHOD, match
        return NO_PATH, None

    def route_request(self, request):
        endpoint, path_match = self.match_request(request)
        try:
            if endpoint is NO_PATH:
                raise _response.NotFound()
            if endpoint is NO_METHOD:
                raise _response.MethodNotAllowed()
            return endpoint(request, path_match)
        except _response.HttpError as err:
            return err.to_response()


class Method(object):
    def __init__(self, *args):
        self.methods = frozenset(arg.upper() for arg in args)

    def matches(self, method):
        """Test if a method matches this Method object.

        ``method`` MUST be uppercased prior to calling this function.
        """
        return method in self.methods


GET = Method('GET')
PUT = Method('PUT')
DELETE = Method('DELETE')
POST = Method('POST')
