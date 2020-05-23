import unittest, os
from journalmk.__main__ import main


class TestMain(unittest.TestCase):

    def test_chronological(self):
        os.chdir(os.path.join("..", "example", "journal_chronological"))
        main()

    def test_topological(self):
        os.chdir(os.path.join("..", "example", "journal_topological"))
        main()

    def test_chronological_matplotlib(self):
        os.chdir(os.path.join("..", "example", "journal_chronological_matplotlib"))
        main()
