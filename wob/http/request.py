from . import message as _message
from . import path as _path


class Request(_message.HttpMessage):
    def __init__(self, method, application_path, path, headers):
        super(Request, self).__init__(headers)
        self.method = method
        self.application_path = _path.Path(application_path).canonicalize()
        self.path = _path.Path(path).canonicalize()

    def copy(self):
        return Request(
            self.method,
            str(self.application_path),
            str(self.path),
            self.headers.copy(),
        )

    @property
    def user_agent(self):
        return _magic_headers.UserAgent(self.headers.get('User-Agent'))

    def sub_request_for_application(self, app_root):
        new_path = self.path.strip_prefix(app_root)
        new_request = self.copy()
        new_request.path = new_path
        new_request.application_path = app_root
        return new_request


class WsgiRequest(Request):
    def __init__(self, wsgi_environment):
        headers = _message.headers_from_wsgi_environment(wsgi_environment)
        method = wsgi_environment['REQUEST_METHOD']
        application_path = wsgi_environment['SCRIPT_NAME'] or '/'
        path = wsgi_environment['PATH_INFO']

        super(WsgiRequest, self).__init__(
            method, application_path, path, headers,
        )
        self.wsgi_environment = wsgi_environment


def request_from_wsgi(environment):
    return WsgiRequest(environment)
