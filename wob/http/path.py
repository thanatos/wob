"""Representation of a path in a URL."""

import itertools as _itertools
import re as _re

import six as _six


_SLASHES = _re.compile('/+')


class Path(object):
    """A path in a URI."""

    def __init__(self, path):
        if not path.startswith('/'):
            raise PathNotAbsolute(path)
        self.text = path

    def __str__(self):
        return self.text

    def __repr__(self):
        return '{}.{}({!r})'.format(
            __name__, type(self).__name__,
            self.text,
        )

    def __eq__(self, other):
        self_canon = self.canonicalize()
        other_canon = other.canonicalize()
        zipped_parts = _six.moves.zip_longest(
            self_canon.components, other_canon.components,
        )
        for self_part, other_part in zipped_parts:
            if self_part != other_part:
                return False
        return True

    def __ne__(self, other):
        return not (self == other)

    @property
    def components(self):
        """Returns an iterator over the components of the path.

        The returned iterator returns one string for each component (the parts
        between the "/"s) of the path. The root is represented by the special
        string ''.

        >>> list(Path('/a/b/c').components)
        ['', 'a', 'b', 'c']
        >>> list(Path('/a/b/c/').components)
        ['', 'a', 'b', 'c']
        >>> list(Path('/').components)
        ['']

        :returns: An iterator over the components of the path.
        """
        slashes_match = _SLASHES.match(self.text)
        if slashes_match is not None and slashes_match.end() == len(self.text):
            # This is a path that represents the root.
            # e.g, '/', '//', '///', etc.
            return iter(('',))
        else:
            return _itertools.chain(
                ('',),
                _SLASHES.split(self.text.strip('/')),
            )

    def canonicalize(self):
        """Canonicalize a path.

        This does the following:

        * Condenses multiple slashes: e.g., /foo/bar and /foo//bar are the
          same. (This goes for the beginning, i.e., that //foo/bar and /for/bar
          are the same.)
        * Processes ".." as a path component as "up a directory", or
          that it removes the preceding component. I.e., /foo/../bar and /bar
          are equivalent.
        * Processes "." as a path component as "this directory". I.e.,
          /foo/./bar and /foo/bar are equivalent.
        """
        parts = _SLASHES.split(self.text.strip('/'))
        remaining_parts = []
        for part in parts:
            if part == '.':
                continue
            elif part == '..':
                if not remaining_parts:
                    raise ValueError(
                        'URL contained a ".." component that could not be'
                        ' applied, because it would traverse higher than "/".'
                    )
                remaining_parts.pop()
            else:
                remaining_parts.append(part)

        new_path = '/' + '/'.join(remaining_parts)
        return Path(new_path)

    def startswith(self, prefix):
        zipped_paths = _itertools.zip_longest(
            self.components,
            prefix.components,
        )
        for our_path, prefix in zipped_paths:
            if prefix is None:
                return True
            if our_path != prefix:
                return False
        return True

    def strip_prefix(self, prefix):
        """Strip a prefix from this Path."""
        zipped_paths = _itertools.zip_longest(
            self.components,
            prefix.components,
        )
        new_path = []
        for our_path, prefix_path in zipped_paths:
            if prefix_path is None:
                new_path.append(our_path)
                new_path.extend(our_path for our_path, _ in zipped_paths)
                break

            if our_path != prefix_path:
                raise ValueError('{!r} didn\'t start with prefix {!r}'.format(
                    self, prefix,
                ))

        return Path('/' + '/'.join(new_path))


class PathNotAbsolute(ValueError):
    def __init__(self, path):
        self.path = path
        super(PathNotAbsolute, self).__init__(path)
