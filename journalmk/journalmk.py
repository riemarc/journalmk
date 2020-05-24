import os, json, hashlib, subprocess, datetime, pathlib, operator, platform, collections

metadata_fname = "journalmk.json"

document_preamble = r"""
\documentclass{scrreprt}

\usepackage{minitoc}
\renewcommand*{\partheadstartvskip}{%
  \null\vskip20pt
}
\renewcommand*{\partheadendvskip}{%
  \vskip2pt
}
\renewcommand\beforeparttoc{}

\usepackage{pdfpages}

\usepackage{color}

\usepackage{datetime}
\ddmmyyyydate

\usepackage{hyperref}
\hypersetup{linktoc=all, colorlinks=false, linkbordercolor={white}}

\makeatletter
\newcommand*\addsubsec{\secdef\@addsubsec\@saddsubsec}
\newcommand*{\@addsubsec}{}
\def\@addsubsec[#1]#2{\subsection*{#2}\addcontentsline{toc}{subsection}{#1}
  \if@twoside\ifx\@mkboth\markboth\markright{#1}\fi\fi
}
\newcommand*{\@saddsubsec}[1]{\subsection*{#1}\@mkboth{}{}}
\makeatother

\title{Notebook}
\author{created with journalmk}
\date{\today\\\currenttime}
"""

document_begin_str = r"""
\begin{document}
\maketitle

\doparttoc[n]
\dominitoc

\pdfbookmark{\contentsname}{Contents}
\tableofcontents
"""

part_str = r"""
\addpart{{{part}}}
\parttoc
"""

chapter_str = r"""
\addchap{{{chapter}}}
\minitoc
"""

sec_toc_str = "1,addsec,1,{{{section}}},sec{label}"

subsec_toc_str = "1,addsubsec,1,{{{subsection}}},subsec{label}"

subsection_str = r"""
\includepdf[
    pages=-,
    addtotoc={{{addtotoc}}},
    picturecommand*={{%
        \put(10,10){{\href{{run:{path}}}{{{datetime} {{\color{{gray}}-- \texttt{{{path_text}}}}}}}}}%
    }}]{{{file}}}
"""

document_end_str = r"""
\end{document}
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


def find_notes(note_dirs, note_endings, exclude_note_endings):

    for note_dir in note_dirs:
        notes = list()
        notes_tmp = list()
        for note in os.listdir(note_dir):
            note_path = os.path.join(note_dir, note)
            is_file = os.path.isfile(note_path)
            is_note = any([note.endswith(ne) for ne in note_endings])
            exclude = any([note.endswith(ene) for ene in exclude_note_endings])
            if is_file and is_note and not exclude:
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


def make_pdf_note(note, pdf, pdf_commands):

    notes_ending = [ne for ne in pdf_commands if note.endswith(ne)][0]
    pdf_command = pdf_commands[notes_ending]

    if not os.path.exists("tmp"):
        os.mkdir("tmp")

    command_tmp = pdf_command.split(" ")
    command = list()
    for cmd_part in command_tmp:
        if "{" + notes_ending + "}" == cmd_part:
            command.append(note)
        elif "{pdf}" == cmd_part:
            command.append(pdf)
        else:
            command.append(cmd_part)

    subprocess.run(command)


def make_pdf_notes(note_dirs, pdf_commands):

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
                make_pdf_note(note, note_tmp, pdf_commands)


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


def get_subsections(note_dirs, formats, metadata=False):

    if metadata:
        note_dirs = parse_metadata(note_dirs)

    subsections = list()
    for nd in note_dirs.values():
        md = nd["metadata"]
        for note, pdf, ts in zip(nd["notes"], nd["pdfs"], nd["timestamps"]):
            if metadata:
                subsection = (note, pdf, ts, md)
            else:
                subsection = (note, pdf, ts)
            subsections.append(
                (ts.strftime(formats["datetime_journal_format"]), subsection))
    subsections = sorted(subsections, key=lambda it: it[1][2], reverse=True)

    return subsections


def get_chronological_document_tree(note_dirs, formats):

    subsections = get_subsections(note_dirs, formats)

    unique_sec = "%W %Y"
    sections = list({s[1][2].strftime(unique_sec) for s in subsections})
    sections = dict([(s, list()) for s in sorted(sections, reverse=True)])
    for ss, (nt, pf, ts) in subsections:
        section = ts.strftime(unique_sec)
        sections[section].append((ss, (nt, pf, ts)))
    sections = [
        (v[0][1][2].strftime(formats["week_number_format"]), v)
        for _, v in sections.items()]

    unique_chap = "%B %Y"
    chapters = list({s[1][2].strftime(unique_chap) for s in subsections})
    chapters = dict([(c, list()) for c in sorted(chapters, reverse=True)])
    for sec, subsecs in sections:
        chapter = subsecs[0][1][2].strftime(unique_chap)
        chapters[chapter].append((sec, subsecs))
    chapters = [
        (v[0][1][0][1][2].strftime(formats["month_year_journal_format"]), v)
        for _, v in chapters.items()]

    unique_part = "%Y"
    parts = list({s[1][2].strftime(unique_part) for s in subsections})
    parts = dict([(part, list()) for part in sorted(parts, reverse=True)])
    for chap, secs in chapters:
        part = secs[0][1][0][1][2].strftime(unique_part)
        parts[part].append((chap, secs))
    parts = [
        (v[0][1][0][1][0][1][2].strftime(formats["year_journal_format"]), v)
        for _, v in parts.items()]

    return parts


def get_topological_document_tree(note_dirs, formats):

    sections = get_subsections(note_dirs, formats, metadata=True)

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

    try:
        with open("journal_template.tex", "r") as file:
            document.write(file.read())
    except Exception as e:
        print(e)
        document.write(document_preamble)

    document.write(document_begin_str)
    for part, chapters in document_tree:
        document.write(part_str.format(part=part))
        for chapter, sections in chapters:
            if chapter is not None:
                document.write(chapter_str.format(chapter=chapter))
            for section, subsections in sections:
                label = pathlib.Path(subsections[0][1][1]).stem
                add_to_toc = [sec_toc_str.format(section=section, label=label)]
                for subsection in subsections:
                    label = pathlib.Path(subsection[1][1]).stem
                    add_to_toc.append(subsec_toc_str.format(
                        subsection=subsection[0],
                        label=label))
                    print(add_to_toc)
                    document.write(subsection_str.format(
                        section=subsection[0],
                        addtotoc=", ".join(add_to_toc),
                        datetime=subsection[0],
                        path=subsection[1][0],
                        path_text=subsection[1][0].replace("_", "\\_"),
                        file=subsection[1][1]
                    ))
                    add_to_toc = list()

    document.write(document_end_str)
    document.close()


def open_journal():

    if platform.system() == "Darwin":
        subprocess.run(["open", "journal.pdf"])

    elif platform.system() == "Windows":
        os.startfile("journal.pdf")

    elif platform.system() == "Linux":
        subprocess.run(["xdg-open", "journal.pdf"])

    else:
        raise NotImplementedError


# https://strftime.org/
formats = dict(datetime_journal_format="%d. %B %Y -- %H:%M",
               datetime_filename_format="%Y-%m-%d-Note-%H-%M",
               week_number_format="Week %W",
               month_year_journal_format="%B",
               year_journal_format="%Y")


def update_formats(conf):
    f = formats.copy()

    def update_format(ff, key):
        if key in conf:
            ff[key] = conf[key]

        return ff

    f = update_format(f, "datetime_journal_format")
    f = update_format(f, "datetime_filename_format")
    f = update_format(f, "week_number_format")
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

    if not "exclude_note_endings" in conf:
        conf.update({"exclude_note_endings": []})

    note_dirs = find_notes(note_dirs,
                           conf["notes_pdf_export_commands"],
                           conf["exclude_note_endings"])

    make_pdf_notes(note_dirs, conf["notes_pdf_export_commands"])

    note_dirs = parse_timestamps(note_dirs, formats)

    note_dirs = parse_metadata(note_dirs)

    document_tree = get_document_tree(note_dirs, conf["journal_type"], formats)

    write_tex_file(document_tree)

    subprocess.run(["latexmk", "-norc", "-pdf", "journal.tex"])

    open_journal()
