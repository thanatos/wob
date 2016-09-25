from . import message as _message
from . import response as _response


class HttpError(Exception):
    def __init__(self, status_code, reason_phrase=None, args=()):
        super(HttpError, self).__init__(*args)

        # None means that the subclass is declaring the status code on the
        # class.
        if status_code is not None:
            self.status_code = status_code
        # None means that the subclass is either declaring the reason phrase on
        # the class, or allowing the default property defined on this class to
        # look it up dynamically.
        if reason_phrase is not None:
            self.reason_phrase = reason_phrase

    @property
    def reason_phrase(self):
        return _response.STATUS_TO_REASON_PHRASE[self.status_code]

    def extra_headers(self):
        return _message.Headers()


def _error_class(class_name, status_code):
    type_ = type(
        class_name, (HttpError,),
        {
            'status_code': status_code,
        },
    )

    def __init__(self):
        super(type_, self).__init__(None)

    type_.__init__ = __init__
    return type_


def to_simple_text_response(error):
    body = '{} {}\n'.format(error.status_code, error.reason_phrase)
    body = body.encode('utf-8')

    headers = _message.Headers()
    headers.add_header('Content-Type', 'text/plain; charset=utf-8')
    headers.extend_headers(error.extra_headers())

    return _response.Response(
        error.status_code,
        error.reason_phrase,
        headers,
        body,
    )


class MethodNotAllowed(HttpError):
    status_code = 405

    def __init__(self, allow):
        super(MethodNotAllowed, self).__init__(args=(self.allow,))
        self.allow = allow

    def extra_headers(self):
        return _message.Headers((
            ('Allow', ', '.join(sorted(self.allow))),
        ))


class NotFound(HttpError):
    status_code = 404


BadRequest = _error_class('BadRequest', 400)
PaymentRequired = _error_class('PaymentRequired', 402)
Forbidden = _error_class('Forbidden', 403)
# NotFound, 404, above.
# MethodNotAllowed, 405, above.
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
