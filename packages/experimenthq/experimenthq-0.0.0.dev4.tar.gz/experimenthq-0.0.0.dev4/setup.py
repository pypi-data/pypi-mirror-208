#!/usr/bin/env python

import os
import re
from glob import glob
from os.path import basename, splitext
from pathlib import Path

from setuptools import find_packages, setup  # type: ignore

# TODO: Update the package meta-data
NAME = "experimenthq"
MAIN_PACKAGE = "experimenthq"
DESCRIPTION = "A Python package for tracking experiments in Notion"
EMAIL = ""
AUTHOR = ""
LICENSE = "MIT"
REQUIRES_PYTHON = ">=3.7"
VERSION = None  # Only set version if you like to overwrite the version in _about.py
WEBSITE = "https://www.experiment-hq.com/"


PWD = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Extract the version from the _about.py module.
if not VERSION:
    with open(os.path.join(PWD, "src", MAIN_PACKAGE, "_about.py")) as f:  # type: ignore
        VERSION = re.findall(r"__version__\s*=\s*\"(.+)\"", f.read())[0]

# Where the magic happens:
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    license=LICENSE,
    packages=find_packages(where="src", exclude=("tests", "test", "examples", "docs")),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    zip_safe=False,
    install_requires=["requests", "types-requests"],
    extras_require={
        # extras can be installed via: pip install package[dev]
        "dev": [
            "pytest",
            "pytest-cov",
            "flake8",
            "black",
            "isort",
            "mypy",
            "twine",
            "wheel",
            "setuptools",
            "build",
            "colorama",
            "types-requests",
        ],
    },
    include_package_data=True,
    package_data={
        # If there are data files included in your packages that need to be
        # 'sample': ['package_data.dat'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Utilities",
    ],
    project_urls={
        "Website": WEBSITE,
    },
    # entry_points={"console_scripts": [f"{NAME}={MAIN_PACKAGE}._cli:cli"]},
    keywords=[
        "notion",
        "tracking",
        "ml",
        "machine learning",
        "experiment",
        "experimentation",
        "experiment tracking",
        "python",
        "sync",
    ],
)
