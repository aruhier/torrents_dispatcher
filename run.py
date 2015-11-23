#!/usr/bin/env python

"""
Torrents distributor
"""

import logging
from config import TORRENT_GROUPS

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for t in TORRENT_GROUPS:
        t.move(dryrun=True)
