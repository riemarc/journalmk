import unittest, os, subprocess
from journalmk.__main__ import main

paths = dict(
    chrono=["..", "example", "journal_chronological"],
    topo=["..", "example", "journal_topological"],
    topo_libre=["..", "example", "journal_topological_libreoffice"],
    chrono_mpl=["..", "example", "journal_chronological_matplotlib"])
for key, path in paths.items():
    paths[key] = os.path.abspath(os.path.join(*path))


class TestMain(unittest.TestCase):

    def test_chronological(self):
        os.chdir(paths["chrono"])
        subprocess.run(["latexmk", "-c"])
        main()

    def test_topological(self):
        os.chdir(paths["topo"])
        subprocess.run(["latexmk", "-c"])
        main()

    def test_chronological_matplotlib(self):
        os.chdir(paths["chrono_mpl"])
        subprocess.run(["latexmk", "-c"])
        main()

    def test_topological_libreoffice(self):
        os.chdir(paths["topo_libre"])
        subprocess.run(["latexmk", "-c"])
        main()
