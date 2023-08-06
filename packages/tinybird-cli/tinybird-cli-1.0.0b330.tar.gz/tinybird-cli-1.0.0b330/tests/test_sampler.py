import unittest

from tinybird.sampler import guess


class TestSampler(unittest.TestCase):

    def test_guess_simple(self):
        self.maxDiff = None
        guessed = []
        guess('my_user', 'my_ds', guessed, {'x': 3, 'y': 'wadus'}, 123)
        self.assertEqual([
            ('my_user', 'my_ds', 123, '$', 'object', 0, ''),
            ('my_user', 'my_ds', 123, '$.x', 'number', 3, ''),
            ('my_user', 'my_ds', 123, '$.y', 'string', 0, 'wadus')
        ], guessed)

    def test_guess_nested(self):
        self.maxDiff = None
        guessed = []
        guess('my_user', 'my_ds', guessed, {'x': {'y': 4}}, 123)
        self.assertEqual([
            ('my_user', 'my_ds', 123, '$', 'object', 0, ''),
            ('my_user', 'my_ds', 123, '$.x', 'object', 0, ''),
            ('my_user', 'my_ds', 123, '$.x.y', 'number', 4, '')
        ], guessed)
