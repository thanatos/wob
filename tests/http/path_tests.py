import doctest
import unittest

from wob.http import path


def load_tests(loader, tests, pattern):
    _ = loader, pattern
    tests.addTests(doctest.DocTestSuite(path))
    return tests


class PathTestCase(unittest.TestCase):
    def test_eq_operator(self):
        self.assertTrue(path.Path('/') == path.Path('///'))
        self.assertTrue(path.Path('/a/b/c') == path.Path('//a///b/c/'))
        self.assertFalse(path.Path('/a') == path.Path('/a/b'))

    def test_ne_operator(self):
        self.assertTrue(path.Path('/a/b/c') != path.Path('/d/e/f'))
        self.assertFalse(path.Path('/a/b/c') != path.Path('/a/b/c'))

    def test_components(self):
        self.assertSequenceEqual(
            ('', 'a', 'b', 'c'), list(path.Path('/a/b/c').components),
        )
        self.assertSequenceEqual(
            ('', 'a', 'b', 'c'), list(path.Path('/a//b//c/').components),
        )
        self.assertSequenceEqual(('',), list(path.Path('/').components))
        self.assertSequenceEqual(('',), list(path.Path('///').components))


if __name__ == '__main__':
    unittest.main()
