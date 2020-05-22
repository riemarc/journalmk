import os, json, hashlib, subprocess, datetime, pathlib, operator, platform

metadata_fname = "journalmk.json"

document_begin_str = r"""
\begin{document}
\maketitle

\doparttoc[n]
\dominitoc

\pdfbookmark{\contentsname}{Contents}
\tableofcontents
"""

document_end_str = r"""
\end{document}
"""

part_str = r"""
\addpart{{{part}}}
\parttoc
"""

chapter_str = r"""
\addchap{{{chapter}}}
\minitoc
"""

section_str = r"""
\includepdf[
    pages=-,
    addtotoc={{1,addsec,1,{{{section}}},{label}}},
    picturecommand*={{%
        \put(10,30){{}}%
        \put(10,10){{\href{{run:{path}}}{{{datetime} {{\color{{gray}}-- \texttt{{{path_text}}}}}}}}}%
           }}]{{{file}}}
"""


def find_directories(root, notes_dir_name, exclude_directories):

    if not os.path.isdir(root):
        raise ValueError(f"'{root}' is not a directory")

    note_dirs = dict()

    for (dir_path, dir_names, file_names) in os.walk(root):
        if any([dir_path.startswith(edp) for edp in exclude_directories]):
            continue

        if notes_dir_name in dir_names:
            notes_path = os.path.join(dir_path, notes_dir_name)
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
                note_tmp_path = os.path.abspath(note_tmp_path)

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


def get_chronological_document_tree(note_dirs):

    notes = list()
    for nd in note_dirs.values():
        for note, pdf, ts in zip(nd["notes"], nd["pdfs"], nd["timestamps"]):
            notes.append([note, pdf, ts])

    n_notes = sum([len(nt["notes"]) for nt in note_dirs.values()])
    if n_notes != len(notes):
        raise ValueError("Something went wrong!")

    notes.sort(key=operator.itemgetter(2))

    parts = list({e[2].strftime("%Y") for e in notes})

    chapters = dict()
    while True:

        try:
            entry = notes.pop()
        except IndexError:
            break
        chapter_name = entry[2].strftime("%B %Y")
        chapters.update({chapter_name: list()})
        section_name = entry[2].strftime("%d. %B %Y -- %H:%M")
        chapters[chapter_name].append((section_name, entry))
        while True:
            if len(notes) == 0:
                break

            if entry[2].year == notes[-1][2].year:
                if entry[2].month == notes[-1][2].month:
                    entry = notes.pop()
                    section_name = entry[2].strftime("%d. %B %Y -- %H:%M")
                    chapters[chapter_name].append((section_name, entry))
                else:
                    break
            else:
                break

    n_sections = sum([len(ch) for ch in chapters.values()])
    if n_notes != n_sections:
        raise ValueError("Something went wrong!")

    parts = dict([(part, list()) for part in sorted(parts, reverse=True)])
    for chapter_name, chapter in chapters.items():
        part = chapter[0][1][2].strftime("%Y")
        parts[part].append((chapter_name, chapter))

    return parts


def get_document_tree(note_dirs, journal_type):

    if journal_type == "chronological":
        return get_chronological_document_tree(note_dirs)

    elif journal_type == "tree":
        raise NotImplementedError

    else:
        raise NotImplementedError


def write_tex_file(document_tree):

    document = open("journal.tex", "w")

    with open("journal_template.tex", "r") as file:
        document.write(file.read())

    document.write(document_begin_str)
    for part, chapters in document_tree.items():
        document.write(part_str.format(part=part))
        for chapter, sections in chapters:
            document.write(chapter_str.format(chapter=chapter))
            for section in sections:
                document.write(section_str.format(
                    section=section[0],
                    label=pathlib.Path(section[1][1]).stem,
                    datetime=section[0],
                    path=section[1][0],
                    path_text=section[1][0].replace("_", "\\_"),
                    file=section[1][1]
                ))

    document.write(document_end_str)
    document.close()


def open_journal():

    if platform.system() == "Darwin":
        subprocess.call(["open", "journal.pdf"])

    elif platform.system() == 'Windows':
        os.startfile("journal.pdf")

    else:
        print(platform.system())
        subprocess.call(["xdg-open", "journal.pdf"])


def make():

    with open("journalmkrc.json") as conf_file:
        conf = json.load(conf_file)

    root_directory = os.path.abspath(os.path.join(*conf["root_directory"]))

    exclude_directories = [os.path.abspath(os.path.join(*path))
                           for path in conf["exclude_directories"]]

    note_dirs = find_directories(root_directory,
                                 conf["notes_directory_name"],
                                 exclude_directories)

    note_dirs = find_notes(note_dirs,
                           conf["notes_file_ending"])

    make_pdf_notes(note_dirs,
                   conf["notes_file_ending"],
                   conf["notes_pdf_export_command"])

    note_dirs = parse_timestamps(note_dirs)

    note_dirs = parse_metadata(note_dirs)

    document_tree = get_document_tree(note_dirs, conf["journal_type"])

    write_tex_file(document_tree)

    subprocess.run(["latexmk", "-norc", "-pdf", "journal.tex"])

    open_journal()
