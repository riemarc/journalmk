import datetime
import hashlib
import json
import operator
import os
import pathlib
import platform
import subprocess
import shutil

metadata_filename = "journalmk.json"

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


def find_directories(root, notes_dir_names, exclude_directories):

    if not os.path.isdir(root):
        raise ValueError(f"'{root}' is not a directory")

    note_dirs = dict()

    for (dir_path, dir_names, file_names) in os.walk(root):
        if any([dir_path.startswith(edp) for edp in exclude_directories]):
            continue

        elif notes_dir_names is None:
            for dir_name in dir_names:
                notes_path = os.path.join(dir_path, dir_name)
                note_dirs.update({notes_path: dict()})

        else:
            for notes_dir_name in notes_dir_names:
                if notes_dir_name in dir_names:
                    notes_path = os.path.join(dir_path, notes_dir_name)
                    note_dirs.update({notes_path: dict()})

    return note_dirs


def parse_timestamp(note_path, period, dt_formats):

    stem = pathlib.Path(note_path).stem
    for fo in dt_formats:
        try:
            ts = datetime.datetime.strptime(stem, fo)
            break
        except ValueError:
            ts = None

    if ts is None:
        ts = datetime.datetime.fromtimestamp(os.path.getctime(note_path))

    if period[0] is not None:
        is_greater = ts >= period[0]
    else:
        is_greater = True

    if period[1] is not None:
        is_less = ts <= period[1]
    else:
        is_less = True

    return ts, is_greater and is_less


def find_notes(note_dirs, note_endings, exclude_note_endings, period, dt_formats):

    for note_dir in note_dirs:
        notes = list()
        notes_tmp = list()
        notes_ts = list()
        for note in os.listdir(note_dir):
            note_path = os.path.join(note_dir, note)
            is_file = os.path.isfile(note_path)
            is_note = any([note.endswith(ne) for ne in note_endings])
            ts, is_in_period = parse_timestamp(note_path, period, dt_formats)
            exclude = any([note.endswith(ene) for ene in exclude_note_endings])
            if is_file and is_note and is_in_period and not exclude:
                note_hash = hashlib.sha224(note_path.encode()).hexdigest()[:30]
                note_tmp_path = os.path.join("tmp", note_hash + ".pdf")
                note_tmp_path = os.path.abspath(note_tmp_path)

                notes.append(note_path)
                notes_tmp.append(note_tmp_path)
                notes_ts.append(ts)

        note_dirs[note_dir].update(notes=notes)
        note_dirs[note_dir].update(pdfs=notes_tmp)
        note_dirs[note_dir].update(timestamps=notes_ts)

    return note_dirs


def parse_metadata(note_dirs):

    for note_dir in note_dirs:
        note_dirs[note_dir].update(metadata=None)
        if metadata_filename in os.listdir(note_dir):
            with open(os.path.join(note_dir, metadata_filename)) as mdf:
                note_dirs[note_dir].update(metadata=json.load(mdf))

    return note_dirs


def make_pdf_note(note, pdf, pdf_commands, inplace_pdf_commands):

    notes_ending = [ne for ne in pdf_commands if note.endswith(ne)][0]
    pdf_command = pdf_commands[notes_ending]

    if not os.path.exists("tmp"):
        os.mkdir("tmp")

    note_path = pathlib.Path(note)
    if note_path.suffix[1:] in inplace_pdf_commands:
        is_inplace_command = True

    command_tmp = pdf_command.split(" ")
    command = list()
    for cmd_part in command_tmp:
        if "{" + notes_ending + "}" == cmd_part:
            command.append(note)
        elif not inplace_pdf_commands and "{pdf}" == cmd_part:
            command.append(pdf)
        elif is_inplace_command and "{outdir}" == cmd_part:
            command.append(os.getcwd())
        else:
            command.append(cmd_part)

    if is_inplace_command:
        command_output = run_command(command)
        src_file = os.path.join(os.getcwd(), note_path.stem + ".pdf")
        shutil.move(src_file, pdf)
        return command_output
    else:
        return run_command(command)


def run_command(command):
    print("Journalmk: Run command '" + " ".join(command) + "'")
    return subprocess.run(command)


def make_pdf_notes(note_dirs, pdf_commands, inplace_pdf_commands):
    failed_processes = list()

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
                completed_process = make_pdf_note(note,
                                                  note_tmp,
                                                  pdf_commands,
                                                  inplace_pdf_commands)
                if completed_process.returncode != 0:
                    failed_processes.append(completed_process)

    return failed_processes


def get_subsections(note_dirs, formats, metadata=False):

    if metadata:
        note_dirs = parse_metadata(note_dirs)

    subsections = list()
    for nd in note_dirs.values():
        if "metadata" in nd:
            md = nd["metadata"]
        else:
            md = None

        for note, pdf, ts in zip(nd["notes"], nd["pdfs"], nd["timestamps"]):
            subsection = (note, pdf, ts, md)

            subsections.append(
                (ts.strftime(formats["datetime_journal_format"]), subsection))

    subsections = sorted(subsections, key=lambda it: it[1][2], reverse=True)

    return subsections


def classify_chronological_entry(entry):
    ts = entry[2]
    part_name = ts.strftime("%Y")
    chapter_name = ts.strftime("%B %Y")
    section_name = ts.strftime("%W %Y")

    return part_name, chapter_name, section_name


def classify_topological_entry(entry):

    md = entry[3]
    unsorted = False
    if md is None:
        unsorted = True
    else:
        if "part" in md:
            part_name = md["part"]
            chapter_name = md["chapter"] if "chapter" in md else None
            section_name = md["section"] if "section" in md else None
        else:
            unsorted = True

    if unsorted:
        ts = entry[2]
        part_name = None
        chapter_name = ts.strftime("%Y")
        section_name = ts.strftime("%B %Y")

    return part_name, chapter_name, section_name


def format_chronological_document_limb(limb, limb_format, subsec_ts):
    limb = [(subsec_ts(v).strftime(limb_format), v)
            for v in sorted(limb.values(), key=subsec_ts, reverse=True)]

    return limb


def format_chronological_document_tree(parts, formats):
    for part, chapters in parts.items():
        for chapter, sections in chapters.items():
            parts[part][chapter] = format_chronological_document_limb(
                sections,
                formats["week_number_format"],
                lambda it: it[0][1][2])

    for part, chapters in parts.items():
        parts[part] = format_chronological_document_limb(
            chapters,
            formats["month_year_journal_format"],
            lambda it: it[0][1][0][1][2])

    parts = format_chronological_document_limb(
        parts,
        formats["year_journal_format"],
        lambda it: it[0][1][0][1][0][1][2])

    return parts


def sort_topological_document_limb(branches, none_index=0):

    none_branch = False
    if None in branches:
        none_branch = branches.pop(None)

    branches = [(b, entries) for b, entries in
                sorted(branches.items(), key=operator.itemgetter(0))]

    if not none_branch == False:
        branches.insert(none_index, (None, none_branch))

    return branches


def sort_topological_document_tree(parts):

    for part, chapters in parts.items():
        for chapter, sections in parts[part].items():
            if part is None:
                parts[part][chapter] = format_chronological_document_limb(
                    sections,
                    formats["month_year_journal_format"],
                    lambda it: it[0][1][2])
            else:
                parts[part][chapter] = sort_topological_document_limb(sections)

    for part, chapters in parts.items():
        if part is None:
            parts[part] = format_chronological_document_limb(
                chapters,
                formats["year_journal_format"],
                lambda it: it[0][1][0][1][2])
        else:
            parts[part] = sort_topological_document_limb(chapters)

    parts = sort_topological_document_limb(parts, none_index=len(parts)-1)

    return parts


def get_document_tree(note_dirs, journal_type, formats, user_formats):

    if journal_type == "topological":
        note_dirs = parse_metadata(note_dirs)

    subsections = get_subsections(note_dirs, formats, metadata=True)

    parts = dict()
    for s, entry in subsections:

        if journal_type == "chronological":
            pn, cn, sn = classify_chronological_entry(entry)
        elif journal_type == "topological":
            pn, cn, sn = classify_topological_entry(entry)
        else:
            raise NotImplementedError

        if pn not in parts:
            parts.update({pn: dict()})

        if cn not in parts[pn]:
            parts[pn].update({cn: dict()})

        if sn not in parts[pn][cn]:
            parts[pn][cn].update({sn: list()})

        parts[pn][cn][sn].append((s, entry))

    if journal_type == "chronological":
        parts = format_chronological_document_tree(parts, user_formats)
    elif journal_type == "topological":
        parts = sort_topological_document_tree(parts)
    else:
        raise NotImplementedError

    return parts


def write_tex_file(document_tree):

    document = open("journal.tex", "w")

    try:
        with open("journal_template.tex", "r") as file:
            document.write(file.read())
    except FileNotFoundError:
        document.write(document_preamble)

    document.write(document_begin_str)
    for part, chapters in document_tree:
        if part is not None:
            document.write(part_str.format(part=part))
        else:
            document.write(part_str.format(part="Unsorted"))
        for chapter, sections in chapters:
            if chapter is not None:
                document.write(chapter_str.format(chapter=chapter))
            for section, subsections in sections:
                label = pathlib.Path(subsections[0][1][1]).stem
                if section is None:
                    add_to_toc = list()
                else:
                    add_to_toc = [sec_toc_str.format(
                        section=section,
                        label=label)]
                for subsection in subsections:
                    label = pathlib.Path(subsection[1][1]).stem
                    add_to_toc.append(subsec_toc_str.format(
                        subsection=subsection[0],
                        label=label))
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
    f = update_format(f, "week_number_format")
    f = update_format(f, "month_year_journal_format")
    f = update_format(f, "year_journal_format")

    return f


def parse_period_date(date_str):
    if date_str is not None:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d--%H-%M")


def parse_period_dates(period):
    if len(period) == 1:
        end = datetime.datetime.today()
        start = end - datetime.timedelta(minutes=period[0])
    elif len(period) == 2:
        start = parse_period_date(period[0])
        end = parse_period_date(period[1])
    else:
        raise NotImplementedError

    return start, end

def make():

    with open("journalmkrc.json") as conf_file:
        conf = json.load(conf_file)

    if "journal_period" not in conf:
        conf.update(journal_period=[None, None])
    else:
        conf["journal_period"] = parse_period_dates(conf["journal_period"])

    root_directory = os.path.abspath(os.path.join(*conf["root_directory"]))

    exclude_directories = [os.path.abspath(os.path.join(*path))
                           for path in conf["exclude_directories"]]

    note_dirs = find_directories(root_directory,
                                 conf["notes_directory_names"],
                                 exclude_directories)

    if "exclude_note_endings" not in conf:
        conf.update({"exclude_note_endings": []})

    pdf_export_commands = dict()
    pdf_export_commands.update(conf["notes_pdf_export_commands"])
    pdf_export_commands.update(conf["notes_pdf_inplace_export_commands"])
    note_dirs = find_notes(note_dirs,
                           pdf_export_commands,
                           conf["exclude_note_endings"],
                           conf["journal_period"],
                           conf["datetime_filename_formats"])

    err_processes = make_pdf_notes(note_dirs,
                                   pdf_export_commands,
                                   conf["notes_pdf_inplace_export_commands"])

    user_formats = update_formats(conf)
    document_tree = get_document_tree(note_dirs,
                                      conf["journal_type"],
                                      formats,
                                      user_formats)

    write_tex_file(document_tree)

    subprocess.run(["latexmk", "-norc", "-pdf", "journal.tex"])

    open_journal()

    if err_processes:
        print("Journalmk: Finished with errors")
        for p in err_processes:
            print("Journalmk: Error in " + str(p))
    else:
        print("Journalmk: Finished")


if __name__ == "__main__":
    make()