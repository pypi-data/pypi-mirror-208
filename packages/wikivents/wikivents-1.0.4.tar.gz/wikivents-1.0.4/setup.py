#!/usr/bin/env python3

import os
import re
from datetime import datetime
from typing import List

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


def get_requirements() -> List[str]:
    req = list()
    with open("requirements.txt") as requirements:
        pattern = re.compile(r"^.*#egg=([\w]+)$")
        for line in requirements.read().splitlines():
            if pattern.match(line):
                req.append(pattern.findall(line)[0])
            else:
                req.append(line)
    return req


exec(open("wikivents/__init__.py").read())

# noinspection PyUnresolvedReferences
setup(
    name="wikivents",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    license="GPLv3 License",
    description="A simple Python package to represent events from Wikipedia and Wikidata resources.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/guilieb/wikivents",
    author="Guillaume Bernard",
    author_email="contact@guillaume-bernard.fr",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=get_requirements(),
)
