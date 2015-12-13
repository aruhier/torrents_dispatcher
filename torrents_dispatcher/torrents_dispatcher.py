from operator import itemgetter
import bencodepy
import glob
import logging
import ntpath
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
    #: name for this dispatcher
    name = None
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

    def describe(self):
        """
        Describe the group
        """
        return (
            "Name: %s\n"
            "Blackholes to watch: %s\n"
            "Watchdirs to target: %s\n"
            "Downloads directories: %s"
            % (self.name or "undefined", self.sources, self.targets,
               self.download_dirs)
        )

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
        logger.debug("%s matches %s" % (torrent, match or "no filter"))
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
            logger.debug("Scanning %s…" % s)
            s = os.path.expanduser(s)
            if os.path.isdir(s):
                files += filter(
                    self.filter, glob.glob(os.path.join(s, "*.torrent"))
                )
            elif os.path.isfile(s):
                if self.filter(s):
                    files.append(s)
            else:
                raise Exception("Cannot read file or directory %s" % s)
        logger.debug("Found %s in \"%s\"" % (files, src))
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
        nb_torrents_moved = 0
        if src is None:
            src = self.sources
        torrents_to_move = [path for s in src for path in self.scan(s)]
        for t, _ in self.have(*torrents_to_move):
            try:
                torrents_to_move.pop(torrents_to_move.index(t))
                logger.info("Torrent \"%s\" already in a wathdir, pass…" % t)
                if not dryrun:
                    try:
                        os.remove(t)
                    except Exception as e:
                        logger.warning("Error when deleting \"%s\"", t)
                        print(e)
            except (ValueError, IndexError):
                pass
            finally:
                if len(torrents_to_move) == 0:
                    break
        for torrent in torrents_to_move:
            target, nb_torrents = min(self.count(), key=itemgetter(1))
            if self.limit == 0 or nb_torrents < self.limit:
                logger.info("Moving %s in %s" % (torrent, target))
                if not dryrun:
                    shutil.move(torrent, target)
                nb_torrents_moved += 1
            else:
                logger.warning("%s cannot be moved, all targets are full."
                               % torrent)
        return nb_torrents_moved

    def _search(self, pattern, dirs, exact_match=False):
        """
        Search a file or pattern in a list of directories

        :param pattern: pattern to search
        :param dirs: directories where searching
        :param exact_match: if True, the filename to match exactly with the
                            pattern (and not only contain it)
        """
        pattern = [pattern] if isinstance(pattern, str) else pattern
        results = [
            os.path.join(os.path.expanduser(d), name)
            for d in dirs
            for name in os.listdir(d)
            if not exact_match and all(
                [word.lower() in name.lower() for word in pattern]
            ) or exact_match and " ".join(pattern) == name
        ]
        return results

    def search_in_watchlist(self, pattern, exact_match=True):
        return self._search(pattern, self.targets, exact_match=True)

    def search(self, pattern, exact_match=False):
        """
        Search for a pattern in download dirs
        """
        return self._search(pattern, self.download_dirs,
                            exact_match=exact_match)

    def _search_multiple_hash(self, torrent_lst, dst_lst):
        """
        Search in a list of hash which ones match with the destination list
        """
        if len(torrent_lst) == 0:
            return
        for dst in dst_lst:
            dst = os.path.expanduser(dst)
            if os.path.isdir(dst):
                logger.debug("Scanning all torrents into %s" % dst)
                for t, h in self._search_multiple_hash(
                    torrent_lst, glob.glob(os.path.join(dst, "*.torrent"))
                ):
                    yield t, h
                return
            try:
                dst_hash = bencodepy.decode_from_file(dst)[b"info"][b"pieces"]
                for t, h in torrent_lst.items():
                    if dst_hash == h:
                        logger.debug("Hash matches for %s", dst)
                        yield t, dst
            except Exception as e:
                logger.error("Error when opening the torrent %s" % dst)
                logger.error(e)

    def search_by_hash(self, torr_hash, *dst):
        """
        Compare a torrent hash with a list of torrents and returns those who
        match
        """
        if not isinstance(torr_hash, bytes):
            torr_hash = torr_hash.encode()
        for d in dst:
            d_hash = bencodepy.decode_from_file(d)[b"info"][b"pieces"]
            if torr_hash == d_hash:
                yield d

    def have(self, *src_lst):
        """
        Check if the torrent is already in a watch directory.

        param src_lst: torrents to scan
        """
        hash_lst = {
            src: bencodepy.decode_from_file(src)[b"info"][b"pieces"]
            for src in src_lst if len(src)
        }
        if not hash_lst:
            return
        logger.debug("Searching if having the list %s…" % hash_lst.keys())
        for src, t in self._search_multiple_hash(hash_lst, self.targets):
            yield (src, t)

    def __init__(self, name=None, sources=None, targets=None,
                 download_dirs=None, filters=None, limit=None,
                 *args, **kwargs):
        self.name = name if name else self.name
        self.sources = sources if sources else self.sources
        self.filters = filters if filters else self.filters
        self.targets = targets if targets else self.targets
        self.limit = limit if limit else self.limit
        self.download_dirs = (download_dirs
                              if download_dirs else self.download_dirs)
