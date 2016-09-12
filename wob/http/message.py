import bisect as _bisect
import collections as _collections

import six as _6


class Headers(object):
    """The headers on an HTTP message.

    This class stores an ordered list of headers that appear on an HTTP request
    or response. It maintains the order of the headers, and stores duplicate
    headers faithfully (i.e., what goes in is exactly what comes out).

    It supports a dict-like interface, but does not inherit from
    ``collections.Mapping`` because it is quirky. (There is no ".values()", for
    example, because I can't imagine any use of it being valid.)
    """
    def __init__(self, headers=()):
        # a list of (key, value) tuples
        self._headers = []
        # map header names to lists of indexes in self._headers where those
        # headers are; this lets us quickly find a header by name.
        self._name_to_index = {}

        self.extend_headers(headers)

    def add_header(self, name, value):
        """Add a single header to the list of headers."""
        self._headers.append((name, value))
        inserted_index = len(self._headers) - 1
        lower_name = name.lower()
        if lower_name in self._name_to_index:
            self._name_to_index[lower_name].append(inserted_index)
        else:
            self._name_to_index[lower_name] = [inserted_index]

    def extend_headers(self, headers):
        if isinstance(headers, (_collections.Mapping, Headers)):
            for name, value in _6.iteritems(headers):
                self.add_header(name, value)
        else:
            for name, value in headers:
                self.add_header(name, value)

    def remove_index(self, index):
        name, _ = self._headers[index]
        del self._headers[index]
        new_names_to_indexes = {}
        for name, indexes in _6.iteritems(self._name_to_index):
            new_indexes = [
                idx if idx < index else idx - 1
                for idx in indexes
                if idx != index
            ]
            new_names_to_indexes[name] = new_indexes
        self._name_to_index = new_names_to_indexes

    def get_all_headers(self, name):
        for index in self._name_to_index[name.lower()]:
            _, value = self._headers[index]
            yield value

    def __getitem__(self, name):
        if name in self:
            return u', '.join(self.get_all_headers(name))
        else:
            raise KeyError(name)

    def get(self, name, default):
        if name in self:
            return u', '.join(self.get_all_headers(name))
        else:
            return default

    def __contains__(self, name):
        return name.lower() in self._name_to_index

    def __iter__(self):
        for name, _ in self._headers:
            yield name

    def __len__(self):
        return len(self._headers)

    if _6.PY3:
        def items(self):
            return iter(self._headers)
    else:
        def iteritems(self):
            return iter(self._headers)

        def items(self):
            return list(self.iteritems())

    def __repr__(self):
        def _headers_repr():
            for header, value in _6.iteritems(self):
                yield '({!r}, {!r})'.format(header, value)

        headers_repr = ', '.join(_headers_repr())
        return '{}.{}([{}])'.format(
            __name__, type(self).__name__,
            headers_repr,
        )

    def __eq__(self, other):
        return self._headers == other._headers

    def __ne__(self, other):
        return self._headers != other._headers


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
