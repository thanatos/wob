import abc as _abc


class Rule(object, metaclass=_abc.ABCMeta):
    @_abc.abstractmethod
    def matches(self, request):
        pass


class Route(object):
    def __init__(self, rule, endpoint):
        self.rule = rule
        self.endpoint = endpoint


class Router(object):
    def __init__(self, routes=()):
        self.routes = list(routes)

    def add_route(self, route):
        self.rules.append(route)

    def match_request_to_route(self, request):
        for route in self.routes:
            match = route.rule.match(request)
            if match is not None:
                return route.endpoint, match
        return None

    def route_request(self, request):
        rule, route_match = self.match_request_to_rule(request)
        if rule is None:
            pass
            # Raise a 404.
        # TODO: the rest
