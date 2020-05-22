import unittest, os
from journalmk.__main__ import main


class TestMain(unittest.TestCase):
    def test_main(self):
        os.chdir(os.path.join("..", "example", "journal"))
        main()
