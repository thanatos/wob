from . import message as _message
from . import path as _path


class Request(_message.HttpMessage):
    def __init__(self, method, path, headers):
        super(Request, self).__init__(headers)
        self.method = method
        self.path = _path.Path(path)
        self.extra = {}

    @property
    def user_agent(self):
        return _magic_headers.UserAgent(self.headers.get('User-Agent'))


class WsgiRequest(object):
    def __init__(self, wsgi_environment):
        headers = _message.headers_from_wsgi_environment(environment)
        method = environment['REQUEST_METHOD']
        path = environment['PATH_INFO']

        super(WsgiRequest, self).__init__(method, path, headers)
        self.extra = wsgi_environment
        self.wsgi_environment = wsgi_environment


def request_from_wsgi(environment):
    headers = _message.headers_from_wsgi_environment(environment)
    method = environment['REQUEST_METHOD']
    path = environment['PATH_INFO']

    return Request(method, path, headers)
