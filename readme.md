Creates a pdf notebook/journal out of journal/xournal/xournalpp/... notes,
using python, latex and the pdf export capabilities of the respective
note taking app.

While it was designed to layout xournalpp notes (*.xopp) well-arranged in a pdf
document, it can be used with all sorts of digital content/notes which have a
pdf representation, like

* pictures (*.jpg, *.png, ...)
* office documents (*.odt, *.doc, *.xls, ...)
* ipynb jupyter notebooks (*.ipynb).
* markup content (*.html, *.svg)

## Quickstart
To build a pdf journal out of your digital notes, just
* create a (preferably) empty directory (the build directory) with a name you like
* place an empty json file, with the name `journalmkrc.json` in the directory
* add the following lines to the json file 
```
jaskdflakd
  akjdflk
```
* [install journalmk](#installation) and execute the command `journalmk` from this directory.

### The source directory of the journal
The directory (the source directory) where journalmk is searching notes can
be specified with the <source-directory> placeholder. The build directory is
not related to the source directory, it can lay inside or outside of the source
directory.

### The directory name(s) for the notes


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

### A pdf in-place conversation command


```
"notes_pdf_inplace_export_commands": {
    "odt": "libreoffice --convert-to pdf {odt}"
},
```

```
"notes_pdf_inplace_export_commands": {
    "odt": "libreoffice --convert-to pdf {odt} --outdir {outdir}"
},
```

The string `"{pdf}"` should not appear in
`notes_pdf_inplace_export_commands` entries and the string `"{outdir}"`
should not appear in `notes_pdf_export_commands` entries,
since they will not be replaced in these scenarios.

### Other controls in the journalmkrc.json
The format of date-related timestamps in the resulting pdf document/journal
can be altered by specifying your preferences in the journalmkrc.json.
These are the default ones:

* `"datetime_journal_format": "%d. %B %Y -- %H:%M"`
* `"week_number_format": "Week %W"`
* `"month_year_journal_format": "%B"`
* `"year_journal_format": "%Y"`

TODO: Keys `"exclude_directories"` and `"period"`

### Summary of all possible controls in journalmkrc.json

### The journal pdf file
TODO: chrono hierarchy, topo hierarchy, file link

## Installation
Journalmk is actually just a python script, but also packaged
and available on the python package index (PyPI). It can be
used without any installation as python script from the command line,
or it can be installed with a package installer, like pip:

* most recent release

```pip```

* from a git tag

```pip```

* from a git repo commit

```pip```

* from local version as editable

```pip```

### Note
The command `journalmk` is only available when the package is installed.
If you want to use it without installation, place `journalmk.py` in the build
directory and execute `python journalmk.py`.

## Requirements
- Python >= 3.8
- LaTex (with packages: latexmk, koma-script, minitoc, pdfpages, graphics, datetime, hyperref)

### Notes
- Tested under Ubuntu 20.04 with Texlive 2019 and Python 3.8.
- It is designed to be cross-platform, but only tested under Linux.