import os, json, hashlib, subprocess, datetime, pathlib

metadata_fname = "journalmk.json"


def find_directories(root, notes_dir_name):

    if not os.path.isdir(root):
        raise ValueError(f"'{root}' is not a directory")

    note_dirs = dict()

    for (dir_path, dir_names, file_names) in os.walk(root):
        if notes_dir_name in dir_names:
            notes_path = os.path.join(dir_path, notes_dir_name)
            if len(os.listdir(notes_path)) != 0:
                note_dirs.update({notes_path: dict()})

    return note_dirs


def find_notes(note_dirs, notes_ending):

    for note_dir in note_dirs:
        notes = list()
        notes_tmp = list()
        for note in os.listdir(note_dir):
            note_path = os.path.join(note_dir, note)
            if note.endswith(notes_ending) and os.path.isfile(note_path):
                note_hash = hashlib.sha224(note_path.encode()).hexdigest()[:30]
                note_tmp_path = os.path.join("tmp", note_hash + ".pdf")

                notes.append(note_path)
                notes_tmp.append(note_tmp_path)

        note_dirs[note_dir].update(notes=notes)
        note_dirs[note_dir].update(pdfs=notes_tmp)

    return note_dirs


def parse_metadata(note_dirs):

    for note_dir in note_dirs:
        note_dirs[note_dir].update(metadata=None)
        if metadata_fname in os.listdir(note_dir):
            with open(os.path.join(note_dir, metadata_fname)) as mdf:
                note_dirs[note_dir].update(metadata=json.load(mdf))

    return note_dirs


def make_pdf_notes(note_dirs, notes_ending, pdf_command):
    for note_dir in note_dirs:
        notes = note_dirs[note_dir]["notes"]
        notes_tmp = note_dirs[note_dir]["pdfs"]
        for note, note_tmp in zip(notes, notes_tmp):
            note_mtime = os.path.getmtime(note)
            if os.path.exists(note_tmp):
                note_tmp_mtime = os.path.getmtime(note_tmp)
                create_pdf = note_tmp_mtime < note_mtime
            else:
                create_pdf = True

            if create_pdf:
                if not os.path.exists("tmp"):
                    os.mkdir("tmp")
                command_tmp = pdf_command.split(" ")
                command = list()
                for cmd_part in command_tmp:
                    if "{" + notes_ending + "}" == cmd_part:
                        command.append(note)
                    elif "{pdf}" == cmd_part:
                        command.append(note_tmp)
                    else:
                        command.append(cmd_part)

                subprocess.run(command)


def parse_timestamps(note_dirs):
    for note_dir in note_dirs:
        timestamps = list()
        for note in note_dirs[note_dir]["notes"]:
            stem = pathlib.Path(note).stem
            # https://strftime.org/
            timestamps.append(datetime.datetime.strptime(stem, "%Y-%m-%d-Note-%H-%M"))

        note_dirs[note_dir].update(timestamps=timestamps)

    return note_dirs


def make_chronological_journal(note_dirs):
    pass


with open("journalmkrc.json") as conf_file:
    conf = json.load(conf_file)

note_dirs = find_directories(conf["root"], conf["notes_directory_name"])
note_dirs = parse_metadata(note_dirs)
note_dirs = find_notes(note_dirs, conf["notes_file_ending"])
make_pdf_notes(note_dirs, conf["notes_file_ending"], conf["notes_pdf_export_command"])
note_dirs = parse_timestamps(note_dirs)
print(note_dirs)

if conf["journal_type"] == "chronological":
    make_chronological_journal(note_dirs)

elif conf["journal_type"] == "tree":
    raise NotImplementedError

else:
    raise NotImplementedError

