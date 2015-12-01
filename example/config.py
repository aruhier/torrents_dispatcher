import glob
import os
from torrents_dispatcher import TorrentsDispatcher

# A torrent folder should not contain more than the defined limit
LIMIT = 1000

GLOBAL_BLACKHOLE = "/mnt/data/torrents/global_blackhole/"

example_com = TorrentsDispatcher(
    name="example.com", sources=[GLOBAL_BLACKHOLE, ],
    filters={"trackers": ["tracker.example.com", ]},
    targets=glob.glob("/mnt/data/torrents/watchdir/rtorrent[0-9]/"),
    download_dirs=glob.glob("/mnt/data/torrents/completed/rtorrent[0-9]/"),
    limit=LIMIT,
)

providers = TorrentsDispatcher(
    name="providers", sources=[os.path.join(GLOBAL_BLACKHOLE, "providers"), ],
    targets=["/mnt/data/torrents/watchdir/rtorrent/providers/", ],
    download_dirs=["/mnt/data/torrents/providers_completed/", ],
    limit=LIMIT,
)

TORRENTS_GROUPS = [example_com, providers]
