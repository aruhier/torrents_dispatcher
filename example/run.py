#!/usr/bin/env python

"""
Torrents distributor
"""

import glob
import os
import logging
from torrents_distributor import TorrentsDistributor

# A torrent folder should not contain more than the defined limit
LIMIT = 1000
DRYRUN = True

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    GLOBAL_BLACKHOLE = "/mnt/data/torrents/global_blackhole/"

    example_com = TorrentsDistributor(
        sources=[GLOBAL_BLACKHOLE, ],
        filters={"trackers": ["tracker.example.com", ]},
        targets=glob.glob("/mnt/data/torrents/watchdir/rtorrent[0-9]/"),
        download_dirs=glob.glob("/mnt/data/torrents/completed/rtorrent[0-9]/"),
        limit=LIMIT,
    )

    providers = TorrentsDistributor(
        sources=[os.path.join(GLOBAL_BLACKHOLE, "providers"), ],
        targets=["/mnt/data/torrents/watchdir/rtorrent/providers/", ],
        download_dirs=["/mnt/data/torrents/providers_completed/", ],
        limit=LIMIT,
    )

    for t in [example_com, providers, ]:
        t.move(dryrun=DRYRUN)
