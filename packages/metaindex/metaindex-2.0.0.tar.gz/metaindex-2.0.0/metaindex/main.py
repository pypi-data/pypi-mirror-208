import argparse
import sys
import time
import datetime
import subprocess
from pathlib import Path

from metaindex import configuration
from metaindex import stores
from metaindex import indexer
from metaindex import indexers
from metaindex import logger
from metaindex import version
from metaindex.cache import Cache
from metaindex.find import find

try:
    from metaindex.fuse import metaindex_fs
except ImportError:
    metaindex_fs = None


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config',
                        default=None,
                        type=str,
                        help="The configuration file to use. Defaults "
                            f"to {configuration.CONFIGFILE}.")

    parser.add_argument('-l', '--log-level',
                        default='warning',
                        choices=['debug', 'info', 'warning', 'error', 'fatal'],
                        help="The level of logging. Defaults to %(default)s.")

    parser.add_argument('--log-file',
                        default=None,
                        type=str,
                        help="Write the log to this file instead of stderr.")

    parser.add_argument('--list',
                        action="store_true",
                        default=False,
                        help="List all available file indexers")

    parser.add_argument('--compact',
                        action="store_true",
                        default=False,
                        help="Compact the database")

    parser.add_argument('-V', '--version',
                        action="version",
                        version='%(prog)s ' + version.__version__,
                        help="Show the version of metaindex and exit")

    subparsers = parser.add_subparsers(dest='command')

    indexparser = subparsers.add_parser('index')

    indexparser.add_argument('-r', '--recursive',
                             default=False,
                             action='store_true',
                             help='Go through all subdirectories of any paths')

    indexparser.add_argument('-f', '--force',
                             default=False,
                             action="store_true",
                             help="Enforce indexing, even if the files on disk "
                                  "have not changed.")

    indexparser.add_argument('-m', '--flush-missing',
                             default=False,
                             type=str,
                             nargs='*',
                             help="Remove files from cache that can no longer be "
                                  "found in the given paths.")

    indexparser.add_argument('-v', '--verbose',
                             default=0,
                             action='count',
                             help="Increase verbosity level. Can be passed "
                                  "multiple times. By default the indexer will "
                                  "be very quiet.")

    indexparser.add_argument('index',
                             nargs='*',
                             type=str,
                             default=False,
                             help="Path(s) to index. If you provide none, all "
                                  "cached items will be refreshed. If you pass "
                                  "- the files will be read from stdin, one "
                                  "file per line.")

    indexparser.add_argument('-p', '--processes',
                             type=int,
                             default=None,
                             help="Number of indexers to run at the same time. "
                                  "Defaults to the number of CPUs that are available.")

    indexparser.add_argument('-C', '--clear',
                             default=False,
                             action='store_true',
                             help="Remove all entries from the cache")

    findparser = subparsers.add_parser('find')

    findparser.add_argument('-t', '--tags',
                            nargs='*',
                            help="Print these metadata tags per file, if they "
                                 "are set. If you provide -t, but no tags, all "
                                 "will be shown.")

    findparser.add_argument('-f', '--force',
                            default=False,
                            action='store_true',
                            help="When creating symlinks, accept a non-empty "
                                 "directory if it only contains symbolic links.")

    findparser.add_argument('-l', '--link',
                            type=str,
                            default=None,
                            help="Create symbolic links to all files inside "
                                 "the given directory.")

    findparser.add_argument('-k', '--keep',
                            default=False,
                            action='store_true',
                            help="Together with --force: do not delete existing "
                                 "links but extend with the new search result.")

    findparser.add_argument('query',
                            nargs='*',
                            help="The search query. If the query is - it will "
                                 "be read from stdin.")

    if metaindex_fs is not None:
        fsparser = subparsers.add_parser('fs')

        fsparser.add_argument('action',
                              choices=('mount', 'unmount', 'umount'),
                              help="The command to control the filesystem")
        fsparser.add_argument('mountpoint',
                              type=str,
                              help="Where to mount the metaindex filesystem.")

    result = parser.parse_args()

    if result.list:
        pass
    elif result.command is None and not result.compact:
        parser.print_help()

    return result


indexed_files_count = 0


def index_status(config, entry):
    global indexed_files_count
    indexed_files_count += 1
    if 0 < config.verbose <= 3:
        print(".", end="", flush=True)
    if config.verbose >= 4:
        print(entry.path)


def run():
    args = parse_args()
    logger.setup(level=args.log_level.upper(), filename=args.log_file)

    config = configuration.load(args.config)

    if args.list:
        for name in sorted(indexer._registered_indexers.keys()):
            print(name)
        return 0

    cache = Cache(config)
    if config.bool(configuration.SECTION_SERVER, configuration.CONFIG_AUTOSTART):
        configfile = configuration.CONFIGFILE
        if args.config is not None:
            configfile = Path(args.config).expanduser()
        attempt = 0
        while not cache.connection_ok() and attempt < 1:
            attempt += 1
            subprocess.Popen(["metaindexserver", "-c", str(configfile), "-d"])
            time.sleep(1)

    if not cache.connection_ok():
        logger.error("Server is not running")
        return -1

    if args.compact:
        cache.compact()

    if args.command == "index":
        if args.clear:
            cache.clear()

        cleanpaths = args.flush_missing
        if args.flush_missing == ['-']:
            cleanpaths = [file_ for file_ in sys.stdin.read().split("\n")
                          if len(file_) > 0]
        elif args.flush_missing == []:
            cleanpaths = None

        # 'None' is a valid parameter for cleanup
        if cleanpaths is not False:
            cache.cleanup(cleanpaths)

        index = args.index
        if index == ['-']:
            index = [file_ for file_ in sys.stdin.read().split("\n")
                     if len(file_) > 0]

        elif index == []:
            index = None

        if args.force:
            cache.expire_metadata(index)

        if index is not False:
            global indexed_files_count
            indexed_files_count = 0

            then = datetime.datetime.now()

            cache.refresh(index,
                          args.recursive,
                          args.processes,
                          callback=lambda e: index_status(args, e))

            if args.verbose > 0:
                feedback = ""
                if args.verbose >= 2:
                    feedback = f"\nIndexed {indexed_files_count} files"
                if args.verbose >= 3:
                    feedback += f" in {datetime.datetime.now() - then}"
                print(feedback)

        return 0

    if args.command == "find":
        return find(cache, args)

    if args.command == 'fs' and metaindex_fs is not None:
        return metaindex_fs(config, args)

    return -1
