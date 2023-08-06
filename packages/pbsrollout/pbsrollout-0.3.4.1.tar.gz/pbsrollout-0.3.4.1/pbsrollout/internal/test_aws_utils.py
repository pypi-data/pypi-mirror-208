from unittest import TestCase

from pbsrollout.internal.aws_utils import get_ecr_images


class Test(TestCase):
    def test_get_ecr_images(self):
        for i in get_ecr_images('pbs'):
            print(i)
