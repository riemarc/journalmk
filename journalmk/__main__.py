from journalmk import *


def main():

    with open("journalmkrc.json") as conf_file:
        conf = json.load(conf_file)

    root_directory = os.path.abspath(os.path.join(*conf["root_directory"]))

    note_dirs = find_directories(root_directory,
                                 conf["notes_directory_name"])

    note_dirs = find_notes(note_dirs,
                           conf["notes_file_ending"])

    make_pdf_notes(note_dirs,
                   conf["notes_file_ending"],
                   conf["notes_pdf_export_command"])

    note_dirs = parse_timestamps(note_dirs)
    note_dirs = parse_metadata(note_dirs)

    if conf["journal_type"] == "chronological":
        document_tree = get_chronological_document_tree(note_dirs)
        make_journal(document_tree)

    elif conf["journal_type"] == "tree":
        raise NotImplementedError

    else:
        raise NotImplementedError

