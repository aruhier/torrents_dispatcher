#!/usr/bin/env python

"""
Torrents distributor
"""

import appdirs
import argparse
import logging
import sys

logger = logging.getLogger()
APP_NAME = "torrents_dispatcher"
sys.path.append(appdirs.user_config_dir(APP_NAME))

try:
    import config
except ImportError:
    logger.critical(
        "Configuration file not found. Please create the file %s" %
        appdirs.user_config_dir(APP_NAME)
    )


def search(parsed_args, *args, **kwargs):
    terms = parsed_args.terms
    hide_groups_name = parsed_args.hide_groups_name
    for t in config.TORRENT_GROUPS:
        results = t.search(terms)
        if not len(results):
            continue
        if not hide_groups_name:
            if t.name:
                print("### Group %s: ###\n" % t.name)
            else:
                print("### Group unnamed: ###\n")
        for r in results:
            print(str.encode(r, errors="ignore").decode())
        if not hide_groups_name:
            print("\n######\n")


def move(dryrun=False, *args, **kwargs):
    nb_moved = sum([t.move(dryrun=dryrun) for t in config.TORRENT_GROUPS])
    if nb_moved:
        logger.debug("All torrents moved")
    else:
        logger.debug("Nothing to move")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Dispatch your torrents to your different watchdirs"
    )

    # Start/Stop/Show command
    sp_action = parser.add_subparsers()
    sp_search = sp_action.add_parser("search", help="search in downloads")
    sp_search.add_argument('terms', metavar='terms', type=str, nargs='+',
                           help='terms to search')
    sp_search.add_argument('-H', '--hide-groups',
                           help="hide group names in the results",
                           dest="hide_groups_name", action="store_true")
    sp_move = sp_action.add_parser(
        "move", help="scan and dispatch the torrent files"
    )

    # Set function to call for each options
    sp_search.set_defaults(func=search)
    sp_move.set_defaults(func=move)

    # Debug option
    parser.add_argument('-d', '--debug', help="set the debug level",
                        dest="debug", action="store_true")
    parser.add_argument('-D', '--dryrun',
                        help="dry run (only used when moving torrents)",
                        dest="dryrun", action="store_true")
    arg_parser = parser

    # Parse argument
    args = arg_parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Execute correct function, or print usage
    if hasattr(args, "func"):
        args.func(parsed_args=args)
    else:
        move(parsed_args=args)
