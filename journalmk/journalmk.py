import os, json, hashlib, subprocess, datetime, pathlib, operator, platform, collections

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


def parse_timestamps(note_dirs, formats):

    for note_dir in note_dirs:
        timestamps = list()
        for note in note_dirs[note_dir]["notes"]:
            stem = pathlib.Path(note).stem
            try:
                ts = datetime.datetime.strptime(
                    stem, formats["datetime_filename_format"])
            except ValueError:
                ts = datetime.datetime.fromtimestamp(os.path.getctime(note))
            timestamps.append(ts)

        note_dirs[note_dir].update(timestamps=timestamps)

    return note_dirs


def get_sections(note_dirs, formats, metadata=False):

    if metadata:
        note_dirs = parse_metadata(note_dirs)

    sections = list()
    for nd in note_dirs.values():
        md = nd["metadata"]
        for note, pdf, ts in zip(nd["notes"], nd["pdfs"], nd["timestamps"]):
            if metadata:
                section = (note, pdf, ts, md)
            else:
                section = (note, pdf, ts)
            sections.append(
                (ts.strftime(formats["datetime_journal_format"]), section))
    sections = sorted(sections, key=lambda it: it[1][2], reverse=True)

    return sections


def get_chronological_document_tree(note_dirs, formats):

    sections = get_sections(note_dirs, formats)

    chapters = list({s[1][2].strftime(formats["month_year_journal_format"]) for s in sections})
    chapters = dict([(c, list()) for c in sorted(chapters, reverse=True)])
    for s, (nt, pf, ts) in sections:
        chapter = ts.strftime(formats["month_year_journal_format"])
        chapters[chapter].append((s, (nt, pf, ts)))

    parts = list({s[1][2].strftime(formats["year_journal_format"]) for s in sections})
    parts = dict([(part, list()) for part in sorted(parts, reverse=True)])
    for chapter in chapters:
        part = chapters[chapter][0][1][2].strftime(formats["year_journal_format"])
        parts[part].append((chapter, chapters[chapter]))

    return parts


def get_topological_document_tree(note_dirs, formats):

    sections = get_sections(note_dirs, formats, metadata=True)

    parts = dict()
    for s, (nt, pf, ts, md) in sections:

        if md is not None and "chapter" in md and "part" not in md:
            pn = "Unsorted"
            cn = ts.strftime(formats["month_year_journal_format"])
        elif md is not None and "chapter" in md and "part" in md:
            pn = md["part"]
            cn = md["chapter"]
        elif md is not None and "chapter" not in md and "part" in md:
            pn = md["part"]
            cn = None
        elif md is not None and "chapter" not in md and "part" not in md:
            pn = "Unsorted"
            cn = ts.strftime(formats["month_year_journal_format"])
        elif md is None:
            pn = "Unsorted"
            cn = ts.strftime(formats["month_year_journal_format"])
        else:
            raise ValueError("Something went wrong!")

        if pn not in parts:
            parts.update({pn: dict()})

        if cn not in parts[pn]:
            parts[pn].update({cn: list()})

        parts[pn][cn].append((s, (nt, pf, ts, md)))

    parts = dict(sorted(parts.items(), key=operator.itemgetter(0)))
    for part in parts:
        none_chap = False
        if None in parts[part]:
            none_chap = parts[part].pop(None)

        parts[part] = collections.OrderedDict(
            sorted(parts[part].items(), key=operator.itemgetter(0),
                   reverse=(part == "Unsorted")))

        if not none_chap == False:
            parts[part].update({None: none_chap})
            parts[part].move_to_end(None, last=False)

        parts[part] = [(cn, secs) for cn, secs in parts[part].items()]

    return parts


def get_document_tree(note_dirs, journal_type, formats):

    if journal_type == "chronological":
        return get_chronological_document_tree(note_dirs, formats)

    elif journal_type == "topological":
        return get_topological_document_tree(note_dirs, formats)

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
            if chapter is not None:
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
        subprocess.run(["open", "journal.pdf"])

    elif platform.system() == "Windows":
        os.startfile("journal.pdf")

    elif platform.system() == "Linux":
        print(platform.system())
        subprocess.run(["xdg-open", "journal.pdf"])

    else:
        raise NotImplementedError


# https://strftime.org/
formats = dict(datetime_journal_format="%d. %B %Y -- %H:%M",
               datetime_filename_format="%Y-%m-%d-Note-%H-%M",
               month_year_journal_format="%B %Y",
               year_journal_format="%Y")


def update_formats(conf):
    f = formats.copy()

    def update_format(ff, key):
        if key in conf:
            ff[key] = conf[key]

        return ff

    f = update_format(f, "datetime_journal_format")
    f = update_format(f, "datetime_filename_format")
    f = update_format(f, "month_year_journal_format")
    f = update_format(f, "year_journal_format")

    return f


def make():

    with open("journalmkrc.json") as conf_file:
        conf = json.load(conf_file)

    formats = update_formats(conf)

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

    note_dirs = parse_timestamps(note_dirs, formats)

    note_dirs = parse_metadata(note_dirs)

    document_tree = get_document_tree(note_dirs, conf["journal_type"], formats)

    write_tex_file(document_tree)

    subprocess.run(["latexmk", "-norc", "-pdf", "journal.tex"])

    open_journal()
