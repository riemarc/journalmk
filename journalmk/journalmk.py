import sys, os, json

metadata_fname = "journalmk.json"


def find_notes_directories(root, notes_dir_name):

    if not os.path.isdir(root):
        raise ValueError(f"'{root}' is not a directory")

    note_dirs = list()

    for (dir_path, dir_names, file_names) in os.walk(root):
        print(dir_path)
        print(dir_names)
        print(file_names)

        if notes_dir_name in dir_names:
            notes_path = os.path.join(dir_path, notes_dir_name)
            if len(os.listdir(notes_path)) != 0:
                note_dirs.append(notes_path)

    return note_dirs


def parse_notes_metadata(note_dirs):

    note_dirs_md = dict()

    for note_dir in note_dirs:
        note_dirs_md.update({note_dir: None})
        if metadata_fname in os.listdir(note_dir):
            with open(os.path.join(note_dir, metadata_fname)) as mdf:
                note_dirs_md[note_dir] = json.load(mdf)

    return note_dirs_md


note_dirs = find_notes_directories(sys.argv[1], sys.argv[2])
note_dirs_md = parse_notes_metadata(note_dirs)
print(note_dirs_md)


