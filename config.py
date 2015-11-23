"""
Configuration file
"""

from torrents_distributor import TorrentsDistributor

# Global #

SRC_BLACKHOLE = "/mnt/nfs/public/Downloads/torrent_files"
TARGET = "/mnt/nfs/private/apps/torrents/"
# A torrent folder should not contain more than the defined limit
LIMIT = 1000
DRYRUN = True

# Blackholes #

what_cd = TorrentsDistributor(
    sources=["/mnt/nfs/public/Downloads/torrent_files/", ],
    filters={"trackers": ["irc.what.cd", ]},
    targets=[
        "/mnt/nfs/private/apps/torrents/rtorrent1/",
        "/mnt/nfs/private/apps/torrents/rtorrent2/",
    ],
    download_dirs=[
        "/mnt/nfs/public/Downloads/Torrents/rtorrent1/",
        "/mnt/nfs/public/Downloads/Torrents/rtorrent2/",
    ], limit=LIMIT,
)

providers = TorrentsDistributor(
    sources=["/mnt/nfs/public/Downloads/torrent_files/providers/", ],
    targets=["/mnt/nfs/private/apps/torrents/rtorrent/providers/", ],
    download_dirs=[
        "/mnt/nfs/public/Downloads/Torrents/providers_completed/",
    ], limit=LIMIT,
)

TORRENT_GROUPS = [what_cd, providers, ]
