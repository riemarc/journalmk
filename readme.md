[![name](https://img.shields.io/pypi/v/journalmk?label=pypi%20package)](https://pypi.org/project/journalmk)
[![name](https://img.shields.io/pypi/dm/journalmk)](https://pypi.org/project/journalmk)

[![name](https://upload.wikimedia.org/wikipedia/commons/6/64/PyPI_logo.svg)](https://pypi.org/project/journalmk)

# Journalmk

Creates a pdf notebook/journal out of journal/xournal/xournalpp/... notes,
using python, latex and the pdf export capabilities of the respective
note taking app.

While it was designed to layout xournalpp notes (*.xopp) well-arranged in a pdf
document, it can be used with all sorts of digital content/notes which can be
converted to a pdf document, like

* pictures (*.jpg, *.png, ...)
* office documents (*.odt, *.doc, *.xls, ...)
* ipynb jupyter notebooks (*.ipynb).
* markup content (*.html, *.svg, ...)

## Quickstart
To build a pdf journal out of your digital notes, just
* create a empty directory (the build directory) with a name you like
* place an empty json file, with the name `journalmkrc.json` in this directory
* add the following lines to this json file 
```
{
    "root_directory": [".."],
    "notes_directory_names": ["_notes"],
    "notes_pdf_export_commands": {
        "xopp": "xournalpp {xopp} -p {pdf}"
    },
    "journal_type": "chronological",
    "datetime_journal_format": "%d. %B %Y -- %H:%M",
}
```
* [install journalmk](#installation) and execute the command `journalmk` from the build directory.

### The root directory of the journal

The directory where journalmk is searching notes (the root directory) can be
specified under the `root_directory` key in the configuration file
`journalmkrc.json`. The build directory can lay inside or outside of the root
directory. Relative paths, as in the example, are relative to the build
directory.

### The directory name(s) for the notes

Under the key `notes_directory_names`, all directory names can be speciefied,
in which notes can be located. Usally, this list is not to long, since in most
cases a user has only one default identifier (for example `_notes`) which is
used system wide, to specify the location where notes can be found.

If no directory name is given, all files under the root directory are considered
as notes.

### The filename format(s) of the notes

The timestamp of a single note will be parsed from the filename. If this fails,
the timestamp will be grabbed from the creation time of the file. While the
latter works fine as long you are always on the same device with the same os,
issues may occur if you switch the one or the other, so it is not recommended
for long time use cases. Timestamp formats can be provided in the
journalmkrc.json, e.g.:
```
"datetime_filename_formats": ["%Y-%m-%d-Note-%H-%M", "Note--%Y-%m-%d--%H-%M"]
```

### A pdf conversation command
For each notes file type a pdf export/conversation command has to be provided.
For xournalpp note, for example, one has to add the respective command in the
following format to the `journalmkrc.json`:
```
"notes_pdf_export_commands": {
  "xopp": "xournalpp {xopp} -p {pdf}"
}
```
The conversation commands for other types of files can be added to this list:
```
"notes_pdf_export_commands": {
  "xopp": "xournalpp {xopp} -p {pdf}",
  "ipynb": "jupyter nbconvert {ipynb} --to pdf --output {pdf}",
  "jpg": "convert {jpg} {pdf}"
}
```
The above placeholder `{xopp}`, `{jpg}`, `{ipynb}` will then be replaced with
the respective filename (full path) of the note and `{pdf}` will be replaced the
pdf filename (full path), to be export.

### A pdf in-place conversation command
For some types of notes no command exists where the full path of the pdf file
can be specified (for example odt files). Instead the respective commands
provide inplace conversation, only. Thes commands has to be provided in the
seperat list:
```
"notes_pdf_inplace_export_commands": {
    "odt": "libreoffice --convert-to pdf {odt}"
},
```
In this list also a output directory can be specified (if necessary):
```
"notes_pdf_inplace_export_commands": {
    "odt": "libreoffice --convert-to pdf {odt} --outdir {outdir}"
},
```
The string `"{pdf}"` should not appear in
`notes_pdf_inplace_export_commands` entries and the string `"{outdir}"`
should not appear in `notes_pdf_export_commands` entries,
since they will not be replaced in these scenarios.

### Notes from a certain period of time
To build a journal with notes from a cetain period of time,
this period can be specified by start and end time, as follows
```
"journal_period": ["2019-03-01--16-30", "2020-03-01--16-30"],
```
or by a time span given in minutes, for example for all notes from the last
half year:
```
"journal_period": [262800]
```

### Ignore files and folders
Directories can be ignored by specifying there full paths,
for example
```
"exclude_directories": [
  ["/", "home", "user", "Projects", "journalmk", "journalmk", "example"]
],
```
and notes can be ignored by specifying there endings, for example
```
"exclude_note_endings": ["autosave.xopp"]
```


## The resulting pdf file

### Hyperlink to the note
At the end of the first page of each note, included in the `journal.pdf`,
a hyperlink to the original source file can be found. By clicking on this
hyperlink the file can be directly opened with the appropriate note taking
application. Therefore, depending on the os, some further system configuration may be
neceessary.

### Journal type
By default the notes will be aligned chronological in the resulting
`journal.pdf` file. To order the notes by topic one can add the following
line to the `journalmkrc.json`:
```
"journal_type": "topological"
```
Therefore, in each notes directory, a additional `journalmk.json` can be
placed to provide the name of the topic (part), subtopic (chapter) and
subsubtopic (section), for example:
```
{
  "part": "Writing",
  "chapter": "Novels",
  "section": "Working title"
}
```
or
```
{
  "part": "Housebuilding",
  "chapter": "Living room",
  "section": "Windows and lightning"
}
```

### Date and time format
The format of timestamps in the resulting pdf document/journal
can be defined in the `journalmkrc.json`.
Default:

* `"datetime_journal_format": "%d. %B %Y -- %H:%M"`
* `"week_number_format": "Week %W"`
* `"month_year_journal_format": "%B"`
* `"year_journal_format": "%Y"`

## Global journalmkrc.json
All configurations which apply user-wide to (almost) all journalmk
projects can be placed in the `.journalmkrc.json` file, located in the
users home directory. These settings will then be loaded for all projects
by default and overwritten with the settings from the
project-specific `journalmkrc.json` file. To ignore this user-wide configuration
file in certain cases, the following line can be added to the
project-specific `journalmkrc.json`:
```
"ignore_user_home_journalmkrc": true
```



## Installation

Journalmk is actually just a python script, but also packaged
and available on the python package index (PyPI). It can be
used without any installation as python script from the command line,
or it can be installed with a package installer, like pip:

* most recent release from PyPI (**recommended**)

```pip install journalmk```

* most recent commit from the master branch

```pip install git+https://github.com/riemarc/journalmk.git```

### Requirements
- Python >= 3.8
- LaTex (with packages: latexmk, koma-script, minitoc, pdfpages, graphics, datetime, hyperref)

### Without installation
The command `journalmk` is only available when the package is installed.
If you want to use  journalmk without installation, place `journalmk.py` in the build
directory and execute `python journalmk.py`.


## Notes
- Tested under Ubuntu 20.04 with Texlive 2019 and Python 3.8.
- Designed to be cross-platform, but only tested under Linux.
