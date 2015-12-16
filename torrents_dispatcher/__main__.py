import appdirs
import argparse
import itertools
import logging
import sys

logger = logging.getLogger()
APP_NAME = "torrents_dispatcher"
sys.path.append(appdirs.user_config_dir(APP_NAME))

try:
    import config
except ImportError:
    logger.critical(
        "Configuration file not found. Please create the file %s." %
        appdirs.user_config_dir(APP_NAME)
    )
    sys.exit(2)


def limit_to_groups(torrents_groups, names):
    if not len(names):
        return torrents_groups
    filtered_groups = [tg for tg in torrents_groups if tg.name in names]
    if not len(filtered_groups):
        logger.warning("No group exists with that name")
    return filtered_groups


def list_groups(parsed_args, *args, **kwargs):
    for t in config.TORRENTS_GROUPS:
        print(t.describe())
        print()


def have(parsed_args, *args, **kwargs):
    torrents = parsed_args.torrents
    hide_groups_name = parsed_args.hide_groups_name
    for t in limit_to_groups(config.TORRENTS_GROUPS, parsed_args.limit_to):
        results = t.have(*torrents)
        try:
            first_result = next(results)
        except StopIteration:
            continue
        if not hide_groups_name:
            if t.name:
                print("### Group %s: ###\n" % t.name)
            else:
                print("### Group unnamed: ###\n")
        for r in itertools.chain([first_result], results):
            print("\"%s\" found in \"%s\"" % r)
        if not hide_groups_name:
            print("\n######\n")


def move(parsed_args, *args, **kwargs):
    dryrun = parsed_args.dryrun
    nb_moved = sum([
        t.move(dryrun=dryrun)
        for t in limit_to_groups(config.TORRENTS_GROUPS, parsed_args.limit_to)
    ])
    if nb_moved:
        logger.debug("All torrents moved")
    else:
        logger.debug("Nothing to move")


def search(parsed_args, *args, **kwargs):
    terms = parsed_args.terms
    hide_groups_name = parsed_args.hide_groups_name
    for t in limit_to_groups(config.TORRENTS_GROUPS, parsed_args.limit_to):
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


def parse_args():
    parser = argparse.ArgumentParser(
        description="Dispatch your torrents to your different watchdirs"
    )

    # Start/Stop/Show command
    sp_action = parser.add_subparsers()

    sp_have = sp_action.add_parser(
        "have",
        help=("check if watch directories already have a torrent with the "
              "same hash")
    )
    sp_have.add_argument('torrents', metavar='torrents', type=str, nargs='+',
                         help='torrents to look for')
    sp_have.add_argument('-H', '--hide-groups',
                         help="hide group names in the results",
                         dest="hide_groups_name", action="store_true")
    sp_have.set_defaults(func=have)

    sp_list = sp_action.add_parser("list", help="list torrent groups")
    sp_list.set_defaults(func=list_groups)

    sp_move = sp_action.add_parser(
        "move", help="scan and dispatch the torrent files"
    )
    sp_move.add_argument('-D', '--dryrun',
                         help="dry run",
                         dest="dryrun", action="store_true")
    sp_move.set_defaults(func=move)

    sp_search = sp_action.add_parser("search", help="search in downloads")
    sp_search.add_argument('terms', metavar='terms', type=str, nargs='+',
                           help='terms to search')
    sp_search.add_argument('-H', '--hide-groups',
                           help="hide group names in the results",
                           dest="hide_groups_name", action="store_true")
    sp_search.set_defaults(func=search)

    parser.add_argument("-l", "--limit", help="limit to group names",
                        dest="limit_to", action="append", default=[])
    # Debug option
    parser.add_argument('-d', '--debug', help="set the debug level",
                        dest="debug", action="store_true")
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
        arg_parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    parse_args()
