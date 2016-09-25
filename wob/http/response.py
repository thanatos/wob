import six as _6

from . import message as _message


class Response(_message.HttpMessage):
    def __init__(self, status_code, reason_phrase, headers, body):
        super(Response, self).__init__(headers)
        self.status_code = status_code
        self.reason_phrase = reason_phrase
        self.headers = headers
        self.body = body

    def return_from_wsgi_app(self, start_response):
        start_response(
            '{} {}'.format(self.status_code, self.reason_phrase),
            list(_6.iteritems(self.headers)),
        )
        if isinstance(self.body, bytes):
            return (self.body,)
        else:
            return self.body

    def __repr__(self):
        return '<{}.{} object at 0x{:x} containing a {} {} response>'.format(
            __name__, type(self).__name__, id(self),
            self.status_code, self.reason_phrase,
        )


def new_response(
        content, mimetype, status_code=200, reason_phrase=None, headers=None):

    if reason_phrase is None:
        if status_code not in STATUS_TO_REASON_PHRASE:
            raise AssertionError(
                '{} is not a status code the library is aware of; if you want'
                ' to use it, you must also supply the reason_phrase argument'
                ' to new_response.'.format(status_code)
            )
        reason_phrase = STATUS_TO_REASON_PHRASE[status_code]
    if headers is None:
        headers = _message.Headers()
    elif not isinstance(headers, _message.Headers):
        headers = _message.Headers(headers)

    if mimetype is not None:
        headers.add_header('Content-Type', mimetype)

    return Response(status_code, reason_phrase, headers, content)


def text_response(
        content, mimetype='text/plain',
        status_code=200, reason_phrase=None, headers=None):

    body = content.encode('utf-8')
    mimetype += '; charset=utf-8'
    return new_response(body, mimetype, status_code, reason_phrase, headers)


STATUS_TO_REASON_PHRASE = {
    100: 'Continue',
    101: 'Switching Protocols',
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    305: 'Use Proxy',
    # 306: '(Unused)',
    307: 'Temporary Redirect',
    400: 'Bad Request',
    # Note: The standard reason-phrase for 401 is "Unauthorized", however, the
    # code semantically means "Unauthenticated", so we deviate from the typical
    # wording to provide the correct meaning.
    401: 'Unauthenticated',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Payload Too Large',
    414: 'URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Range Not Satisfiable',
    417: 'Expectation Failed',
    426: 'Upgrade Required',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
}
