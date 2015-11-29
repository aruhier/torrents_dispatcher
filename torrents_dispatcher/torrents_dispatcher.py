import bencodepy
import glob
import logging
import os
import re
import shutil

logger = logging.getLogger(__name__)


class TorrentsDispatcher():
    """
    Group of torrents to distribute

    Defined by blackholes to use as sources and targets, paths where files are
    downloaded.
    """
    #: blackholes to use as sources
    sources = list()
    #: apply filters on torrents in the backhole source
    filters = dict()
    #: blackholes to use as targets
    targets = list()
    #: limit of torrent in each target. 0 for unlimited
    limit = 0
    #: download dirs, used to search a torrent
    download_dirs = list()

    def count(self, target=None):
        """
        Count how many torrents are in each target

        :param target: optionnal. If indicated, will only count files in it,
                       otherwise will yield a result for each folder in
                       targets.
        :return (target, nb_torrents): yield a tuple
        """
        if target is None:
            folders = self.targets
        else:
            folders = [target] if isinstance(target, str) else target
        for t in folders:
            torr_list = glob.glob(os.path.join(t, "*.torrent"))
            yield (t, len(torr_list))

    def filter(self, torrent):
        """
        Apply filter and return the match as a boolean

        :param torrent: path of torrent file to apply the filters on
        """
        match = True
        if (self.filters.get("trackers", False) and
                len(self.filters["trackers"])):
            try:
                decoded_torrent = bencodepy.decode_from_file(torrent)
                tracker = decoded_torrent[b"announce"].decode()
                logger.debug("Tracker of %s: %s" % (torrent, tracker))
                regex = r"^.*://%s(:\d*|)(/.*|)$"
                if isinstance(self.filters["trackers"], str):
                    match = (
                        match and
                        re.match(regex % self.filters["trackers"], tracker)
                    )
                else:
                    match = (
                        match and
                        any([
                            re.match(regex % f_tracker, tracker)
                            for f_tracker in self.filters["trackers"]
                        ])
                    )
            except Exception as e:
                logger.info(
                    "%s doesn't contain a announce field, pass" % torrent
                )
                logger.debug(e)
                pass
        logger.debug("%s match %s" % (torrent, match))
        return match

    def scan(self, src):
        """
        Scan a directory and returns all files that match with filters
        """
        if src is None:
            src = self.src
        else:
            src = [src] if isinstance(src, str) else src
        files = []
        for s in src:
            if os.path.isdir(s):
                files += filter(
                    self.filter, glob.glob(os.path.join(s, "*.torrent"))
                )
            elif os.path.isfile(s):
                if filter(s):
                    files.append(s)
            else:
                raise Exception("Cannot read file or directory %s" % s)
        return files

    def move(self, src=None, dryrun=False):
        """
        Move all files that match to the targets dirs

        Scans a directory, retains all files that match with the filters (if
        any) and then move them to the first target directory under the limit.

        :param src: directory of file to scan
        :param dryrun: doesn't move files, just show what has been done.
                       Setting the logger level to INFO is needed.
        """
        if src is None:
            src = self.sources
        logger.debug(list())
        for torrent in [path for s in src for path in self.scan(s)]:
            moved = False
            for target, nb_torrents in self.count():
                if self.limit == 0 or nb_torrents < self.limit:
                    logger.info("Moving %s in %s" % (torrent, target))
                    if not dryrun:
                        shutil.move(torrent, target)
                    moved = True
                    break
            if not moved:
                logger.warning("%s cannot be moved, all targets are full."
                               % torrent)

    def __init__(self, sources=None, targets=None, download_dirs=None,
                 filters=None, limit=None, *args, **kwargs):
        self.sources = sources if sources else self.sources
        self.filters = filters if filters else self.filters
        self.targets = targets if targets else self.targets
        self.limit = limit if limit else self.limit
        self.download_dirs = (download_dirs
                              if download_dirs else self.download_dirs)
