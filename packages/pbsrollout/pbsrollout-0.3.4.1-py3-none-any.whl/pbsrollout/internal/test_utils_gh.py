from unittest import TestCase

from pbsrollout.internal.utils_gh import does_gh_cli_exist, get_pr_titles_and_author_from_commit_hash


class Test(TestCase):
    def test_does_gh_cli_exist(self):
        ret = does_gh_cli_exist()
        assert ret

    def test_get_pr_titles_and_author_from_commit_hash(self):
        ret = get_pr_titles_and_author_from_commit_hash(['6d797938e', '0a60da612'])
        for r in ret:
            print(f'{r[0].ljust(18)} - {r[1]} - {r[2]}')
        return

        ret = get_pr_titles_and_author_from_commit_hash('f285a46c4')
        for r in ret:
            print(f'{r[0]} - {r[1]}')
        return
        #
        # ret = get_pr_titles_and_author_from_commit_hash(['93b9fbd94', '378ca4130'])
        # for r in ret:
        #     print(f'{r[0]} - {r[1]}')

        images = ['f285a46c4', '6769a481d', '378ca4130', '6a7571b49', '93b9fbd94', 'e6f421ca6', '68426b2c5', 'd605cb077', 'adc923d78', 'ce12b8fe0']
        ret = get_pr_titles_and_author_from_commit_hash(images)
        for r in ret:
            print(f'{r[0]} - {r[1]} = {r[2]}')
