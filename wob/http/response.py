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
            list(self.headers),
        )
        return (self.body,)


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
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    413: 'Payload Too Large',
    414: 'URI Too Long',
    415: 'Unsupported Media Type',
    417: 'Expectation Failed',
    426: 'Upgrade Required',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
}


class HttpError(Exception):
    def to_response(self):
        body = '{} {}\n'.format(self.status_code, self.reason_phrase)
        body = body.encode('utf-8')
        headers = _message.Headers()
        headers.add_header('Content-Type', 'text/plain; charset=utf-8')
        return Response(
            self.status_code,
            self.reason_phrase,
            headers,
            body,
        )


def _error_class(class_name, status_code):
    return type(
        class_name, (HttpError,),
        {
            'status_code': status_code,
            'reason_phrase': STATUS_TO_REASON_PHRASE[status_code],
        },
    )


BadRequest = _error_class('BadRequest', 400)
PaymentRequired = _error_class('PaymentRequired', 402)
Forbidden = _error_class('Forbidden', 403)
NotFound = _error_class('NotFound', 404)
MethodNotAllowed = _error_class('MethodNotAllowed', 405)
NotAcceptable = _error_class('NotAcceptable', 406)
RequestTimeout = _error_class('RequestTimeout', 408)
Conflict = _error_class('Conflict', 409)
Gone = _error_class('Gone', 410)
LengthRequired = _error_class('LengthRequired', 411)
PayloadTooLarge = _error_class('PayloadTooLarge', 413)
UriTooLong = _error_class('UriTooLong', 414)
UnsupportedMediaType = _error_class('UnsupportedMediaType', 415)
ExpectationFailed = _error_class('ExpectationFailed', 417)
UpgradeRequired = _error_class('UpgradeRequired', 426)
InternalServerError = _error_class('InternalServerError', 500)
NotImplemented_ = _error_class('NotImplemented_', 501)
BadGateway = _error_class('BadGateway', 502)
ServiceUnavailable = _error_class('ServiceUnavailable', 503)
GatewayTimeout = _error_class('GatewayTimeout', 504)
