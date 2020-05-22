from journalmk import *


with open("journalmkrc.json") as conf_file:
    conf = json.load(conf_file)


def main():
    note_dirs = find_directories(conf["root"],
                                 conf["notes_directory_name"])

    note_dirs = find_notes(note_dirs,
                           conf["notes_file_ending"])

    make_pdf_notes(note_dirs,
                   conf["notes_file_ending"],
                   conf["notes_pdf_export_command"])

    note_dirs = parse_timestamps(note_dirs)
    note_dirs = parse_metadata(note_dirs)

    if conf["journal_type"] == "chronological":
        make_chronological_journal(note_dirs)

    elif conf["journal_type"] == "tree":
        raise NotImplementedError

    else:
        raise NotImplementedError

