import setuptools

description = ("Creates a pdf notebook/journal out of your digital notes, using latex + python")

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="journalmk",
    version="2022.1",
    author="Marcus Riesmeier",
    author_email="marcus.riesmeier@umit-tirol.com",
    license="BSD 3-Clause License",
    description=description,
    long_description=description,
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

