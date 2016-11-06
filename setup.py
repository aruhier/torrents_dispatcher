#!/usr/bin/env python3

"""
Dispatch your torrents into multiple watchdirs
See:
    https://github.com/Anthony25/torrents_dispatcher
"""

from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))

setup(
    name="torrents_dispatcher",
    version="0.0.5",

    description="Dispatch your torrents between multiple torrents clients",

    url="https://github.com/Anthony25/torrents_dispatcher",
    author="Anthony25 <Anthony Ruhier>",
    author_email="anthony.ruhier@gmail.com",

    license="Simplified BSD",

    classifiers=[
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: BSD License",
    ],

    keywords="torrent",
    packages=["torrents_dispatcher", ],
    install_requires=["appdirs", "argparse", "bencodepy"],
    entry_points={
        'console_scripts': [
            'torrdispatcher = torrents_dispatcher.__main__:parse_args',
        ],
    }
)
