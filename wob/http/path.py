"""Representation of a path in a URL."""

import re as _re


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

    def __iter__(self):
        slashes_match = _SLASHES.match(self.text)
        if slashes_match is not None and slashes_match.end() == len(self.text):
            return iter(('/',))
        return iter(_SLASHES.split(self.text.strip('/')))

    def __eq__(self, other):
        self_canon = self.canonicalize()
        other_canon = other.canonicalize()
        for self_part, other_part in zip(self_canon, other_canon):
            if self_part != other_part:
                return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def canonicalize(self, trailing_slash):
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
        if trailing_slash:
            new_path += '/'
        return Path(new_path)


class PathNotAbsolute(ValueError):
    def __init__(self, path):
        self.path = path
        super(PathNotAbsolute, self).__init__(path)
