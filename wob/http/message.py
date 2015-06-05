import bisect as _bisect

import six as _6


class Headers(object):
    """The headers on an HTTP message.

    This class stores an ordered list of headers that appear on an HTTP request
    or response.
    """
    def __init__(self, headers=()):
        # a list of (key, value) tuples
        self._headers = []
        # map header names to indexes in self._headers
        self._name_to_index = {}

    def add_header(self, name, value):
        """Add a single header to the list of headers."""
        self._headers.append((name, value))
        lower_name = name.lower()
        if lower_name in self._name_to_index:
            _bisect.insort(
                self._name_to_index[lower_name], len(self._headers) - 1,
            )
        else:
            self._name_to_index[lower_name] = [len(self._headers) - 1]

    def remove_index(self, index):
        name, _ = self._headers[index]
        del self._headers[index]
        self._name_to_index[name.lower()].remove(index)

    def get_all_headers(self, name):
        for index in self._name_to_index[name.lower()]:
            _, value = self._headers[index]
            yield value

    def get(self, name, default=None):
        if name in self:
            return u','.join(self.get_all_headers(name))
        else:
            return default

    def __contains__(self, name):
        return name.lower() in self._name_to_index

    def __iter__(self):
        return iter(self._headers)


def headers_from_wsgi_environment(environ):
    headers = Headers()
    for key, value in environ.items():
        if _6.PY2:
            key = key.decode('latin1')
            value = value.decode('latin1')
        if key.startswith(u'HTTP_'):
            name = key[5:]
            if not name:
                raise ValueError('Malformed WSGI key: ' + key)
            parts = name.split(u'_')

            def recap_parts():
                for part in parts:
                    yield part[0].upper() + part[1:].lower()

            name = u'-'.join(recap_parts())

            headers.add_header(name, value)

    return headers


class HttpMessage(object):
    """Common traits on an HTTP request/response message.

    Headers and body.
    """

    def __init__(self, headers):
        self.headers = headers
