import setuptools
import os

def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        return file.read()

description = ("Creates a pdf notebook/journal out of your digital notes, using latex + python")

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="journalmk",
    version="2022.3",
    url="https://github.com/riemarc/journalmk",
    author="Marcus Riesmeier",
    author_email="gluehen-sierren-0c@icloud.com",
    license="BSD 3-Clause License",
    description=description,
    long_description=read_file('readme.md'),
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ),
    entry_points={
        "console_scripts": ['journalmk=journalmk.__main__:main'],
    }
)

