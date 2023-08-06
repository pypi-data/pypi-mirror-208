import os
import tempfile
import unittest

from utils.Git import Git

TEST_REPO_URL = 'https://github.com/nuuuwan/utils'
TEST_DIR_REPO = tempfile.TemporaryDirectory().name
TEST_BRACH_NAME = 'main'

TEST_GIT = Git(TEST_REPO_URL)


class TestGit(unittest.TestCase):
    def test_clone(self):
        git = TEST_GIT
        git = Git(TEST_REPO_URL)
        git.clone(TEST_DIR_REPO, force=True)

    @unittest.skip('Fails on windows')
    def test_checkout(self):
        git = TEST_GIT
        git.clone(TEST_DIR_REPO, force=True)
        git.checkout(TEST_BRACH_NAME)
        self.assertTrue(os.path.exists(TEST_DIR_REPO))

        git.clone(TEST_DIR_REPO, force=False)
        git.checkout(TEST_BRACH_NAME)

    def test_add_and_commit(self):
        git = TEST_GIT
        git.clone(TEST_DIR_REPO, force=True)
        git.checkout(TEST_BRACH_NAME)
        cmd = f'echo "test" > {TEST_DIR_REPO}/test.txt'
        os.system(cmd)
        git.add_and_commit('test')

    @unittest.skip('Changes repo code')
    def test_push(self):
        git = TEST_GIT
        git.clone(TEST_DIR_REPO, force=True)
        git.checkout(TEST_BRACH_NAME)
        cmd = f'echo "$(date +%Y%m%d-%H%M%S)" > {TEST_DIR_REPO}/test.txt'
        os.system(cmd)
        git.add_and_commit('test')
        git.push()


if __name__ == '__main__':
    unittest.main()
