from setuptools import setup, find_packages
from pathlib import Path

import os

version = "4.0.0+slc.1"

extras_require = {}

setup(
    name="ftw.upgrade",
    version=version,
    description="Transition package to collective.ftw.upgrade.",
    long_description="\n".join(
        [
            Path("README.md").read_text(encoding="utf-8"),
            Path("docs", "HISTORY.md").read_text(encoding="utf-8"),
        ]
    ),
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 6.1",
        "Framework :: Plone :: 6.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Software Development",
    ],
    keywords="plone ftw upgrade",
    author="4teamwork AG",
    author_email="info@4teamwork.ch",
    url="https://github.com/4teamwork/ftw.upgrade",
    license="GPL2",
    packages=find_packages(exclude=["ez_setup"]),
    namespace_packages=["ftw"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "collective.ftw.upgrade",
    ],
    entry_points={
        "z3c.autoinclude.plugin": ["target = plone"],
    },
)
