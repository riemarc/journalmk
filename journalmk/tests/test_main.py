import unittest
from journalmk.__main__ import main
from journalmk.journalmk import *

paths = dict(
    chrono=["..", "..", "examples", "journal_chronological"],
    topo=["..", "..", "examples", "journal_topological"],
    topo_libre=["..", "..", "examples", "journal_topological_libreoffice"],
    chrono_mpl=["..", "..", "examples", "journal_chronological_matplotlib"])
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


class TestFileUpdates(unittest.TestCase):

    def setUp(self):
        import json
        endings = ["home", "error", "notes", "joined", "ignore"]
        self.jmkrcs = dict()
        for ending in endings:
            with open(f"journalmkrc_{ending}.json") as file:
                self.jmkrcs.update({ending: json.load(file)})

    def test_error(self):
        with self.assertRaises(ValueError):
            load_user_journalmkrc("journalmkrc_error.json", os.getcwd())

    def test_update(self):
        jmkrc = load_user_journalmkrc("journalmkrc_home.json", os.getcwd())
        self.assertEqual(jmkrc, self.jmkrcs["home"])
        jmkrc = update_user_journalmkrc(jmkrc,
                                        test_filename="journalmkrc_notes.json")
        self.assertEqual(jmkrc, self.jmkrcs["joined"])

    def test_ignore(self):
        jmkrc = load_user_journalmkrc("journalmkrc_home.json", os.getcwd())
        self.assertEqual(jmkrc, self.jmkrcs["home"])
        jmkrc = update_user_journalmkrc(jmkrc,
                                        test_filename="journalmkrc_ignore.json")
        self.assertEqual(jmkrc, self.jmkrcs["ignore"])


