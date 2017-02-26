"""Routing based on the URL path."""

import abc as _abc
import itertools as _it
import re as _re
import threading as _threading

import six as _6

from ..http import path as _path


REMAINING_COMPONENTS = object()
_END = object()


class PathMatch(object):
    def __init__(self, matched_values, remaining):
        self.matched_values = matched_values
        self.remaining = remaining


class PathRule(object):
    def __init__(self, path_component_handlers, prefer_trailing_slash=False):
        self.path_component_handlers = tuple(path_component_handlers)
        for component_handler in self.path_component_handlers[:-1]:
            if component_handler is REMAINING_COMPONENTS:
                raise ValueError(
                    'REMAINING_COMPONENTS must be the last thing in a list of'
                    ' path component handlers.'
                )
        self.prefer_trailing_slash = prefer_trailing_slash

    def match(self, path):
        """Determines whether this PathRule matches the given path.

        :returns:
            None, if the rule does not match, otherwise, a dictionary
            containing any matched values from the path.
        """

        path = path.canonicalize()

        zipped_path = _it.zip_longest(
            self.path_component_handlers, path.components,
            fillvalue=_END,
        )

        matched_values = {}

        for component_handler, component in zipped_path:
            if component_handler is _END:
                return None
            elif component_handler is REMAINING_COMPONENTS:

                def remaining_components():
                    for _, remaining_component in zipped_path:
                        yield remaining_component

                remaining = _path.Path('/' + '/'.join(remaining_components()))
                matched_values['remaining'] = remaining
                break
            elif component is _END:
                return None
            elif isinstance(component_handler, _6.string_types):
                if component_handler != component:
                    return None
            else:
                try:
                    value = component_handler.parse(component)
                except ValueError:
                    return None
                matched_values[component_handler.name] = value

        return matched_values


# A registry of component handlers, for quick building of PathRule objects.
_global_path_component_handlers = {}
_global_path_component_handlers_lock = _threading.Lock()


def register_path_component_handler(handler_name, handler_class):
    with _global_path_component_handlers_lock:
        # TODO: error if keys don't match.
        _global_path_component_handlers[handler_name] = handler_class


def global_path_component_handler(handler_name):
    def decorator(cls):
        register_path_component_handler(handler_name, cls)
        return cls
    return decorator


_MORE_THAN_ONE_SLASH = _re.compile('/{2,}')
_PATH_RULE_PART = _re.compile('^<(?P<parser>[^:<>]+):(?P<name>[^:<>]+)>$')

def path_rule(input_str, extra_component_handlers={}):
    with _global_path_component_handlers_lock:
        component_handlers = dict(_global_path_component_handlers)
    component_handlers.update(extra_component_handlers)

    if not input_str.startswith('/'):
        raise ValueError(
            'A URL path scheme must be absolute (i.e., start with "/".')

    if _MORE_THAN_ONE_SLASH.search(input_str):
        raise ValueError(
            'A URL path scheme must not contain double slashes.'
        )

    # If the user passes a trailing slash, assume they prefer that form.
    # Record the preference, then strip it out.
    prefer_trailing_slash = input_str.endswith('/')
    if input_str.endswith('/'):
        input_str = input_str[:-1]

    # If this is the root, return early. We represent the root as an empty
    # tuple of path component handlers; the split() call below, however,
    # returns ('',)
    # Note that input_str is changed above, so "root" here is ''.
    if input_str == '':
        return PathRule(('',), prefer_trailing_slash=prefer_trailing_slash)

    # Remove the leading slash.
    input_str = input_str[1:]

    components = input_str.split('/')
    path_components = ['',]
    for component in components:
        if component.startswith('<') and component.endswith('>'):
            component = component[1:-1]
            colon_split_result = component.split(':')
            if len(colon_split_result) != 2:
                raise ValueError(
                    'A component handler specification must be in the form'
                    ' "<NAME: TYPE>".')
            name, handler_type_name = colon_split_result
            handler_type = component_handlers[handler_type_name]
            handler = handler_type(name)
            path_components.append(handler)
        elif component == '**':
            path_components.append(REMAINING_COMPONENTS)
        else:
            path_components.append(component)

    return PathRule(path_components, prefer_trailing_slash)


# Various URL path component handlers below here.
class PathComponentHandler(object):
    def __init__(self, name):
        self.name = name

    @_abc.abstractmethod
    def parse(self, component):
        raise NotImplementedError()

    def normalize(self, component_value):
        return str(component_value)


@global_path_component_handler('string')
class ArbitraryStringHandler(PathComponentHandler):
    def parse(self, component):
        return component


@global_path_component_handler('int')
class IntegerHandler(PathComponentHandler):
    def parse(self, component):
        return int(component, 10)


_UUID = _re.compile(
    '^[0-9A-Za-z]{8}'
    '-[0-9A-Za-z]{4}'
    '-[0-9A-Za-z]{4}'
    '-[0-9A-Za-z]{4}'
    '-[0-9A-Za-z]{12}$'
)


@global_path_component_handler('uuid')
class UuidHandler(PathComponentHandler):
    def parse(self, component):
        # be more strict than the python parser.
        if not _UUID.match(component):
            raise ValueError('Not a UUID.')

        return _uuid.UUID(component)
