Creates a pdf notebook/journal out of your journal/xournal/xournalpp/... notes,
using python, latex and the pdf export capabilities of your note taking app.

While it was designed to layout xournalpp notes (*.xopp) well-arranged in a pdf document,
it can be used with all sorts of digital content/notes which have a pdf representation,
like

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
* and execute the command `journalmk` from this directory.

### The source directory of your journal
The directory (the source directory) where journalmk is searching your notes can
be specified with the <source-directory> placeholder. The build directory is
not related to the source directory, it can lay inside or outside of the source
directory.

### The directory name(s) for your journal note


### The filename format(s) of your notes
The timestamp of a single note will be parsed from the filename. If this fails,
the timestamp will be grabbed from the creation time of the file. While the
latter works fine as long you are always on the same device with the same os, issues
may occur if you switch the one or the other, so it is not recommended for long
time use cases. Timestamps from filenames of the format `%Y-%m-%d-Note-%H-%M`
will be parsed out of the box. If you have differing filename formats, they can
be provided in the journalmkrc.json, e.g.:

* `"datetime_filename_formats": ["Note--%Y-%m-%d--%H-%M", "%Y-%m-%d--%H-%M--Note"]`

### The pdf conversation command

### The pdf conversation command for libreoffice documents

### Other controls in the journalmkrc.json
The format of date-related timestamps in the resulting pdf document/journal
you can alter by specifying your preferences in the journalmkrc.json.
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

### Requirements