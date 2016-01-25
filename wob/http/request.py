from . import message as _message
from . import path as _path


class Request(_message.HttpMessage):
    def __init__(self, method, application_path, path, headers):
        super(Request, self).__init__(headers)
        self.method = method
        if application_path == '':
            self.application_path = None
        else:
            self.application_path = _path.Path(application_path)
        self.path = _path.Path(path)

    @property
    def user_agent(self):
        return _magic_headers.UserAgent(self.headers.get('User-Agent'))


class WsgiRequest(Request):
    def __init__(self, wsgi_environment):
        headers = _message.headers_from_wsgi_environment(wsgi_environment)
        method = wsgi_environment['REQUEST_METHOD']
        application_path = wsgi_environment['SCRIPT_NAME']
        path = wsgi_environment['PATH_INFO']

        super(WsgiRequest, self).__init__(
            method, application_path, path, headers,
        )
        self.wsgi_environment = wsgi_environment


def request_from_wsgi(environment):
    return WsgiRequest(environment)
