from unittest import TestCase

from pbsrollout.internal.utils import is_dev


class Test(TestCase):
    def test_is_dev(self):
        assert is_dev()
