"""The metaindex backend server"""
import argparse
import string
import socketserver
import queue
import csv
import hashlib
import threading
import shutil
import json
import os
import sys
import signal

import xapian

from metaindex import configuration
from metaindex import logger
from metaindex import proto
from metaindex import shared
from metaindex import version
from metaindex.cacheentry import CacheEntry


# xapian value slots
SLOT_FILEPATH = 0
SLOT_LASTMODIFIED = 1

# default human->xapian translations
BASE_TAGS = {
    'path': 'P',
    'filename': 'F',
    'file': 'F',
    'extension': 'E',
    'mimetype': 'T',
    'mime': 'T',
    'author': 'A',
    'date': 'D',
    'title': 'S',
    'language': 'L',
    'subject': 'K',
    'tag': 'K',
    'rel_path': 'XP',
    'storage': 'XSL',
    'fulltext': '',
}
ID_PREFIX = 'Q'


class ConnectionHandler(socketserver.StreamRequestHandler):
    """Handles a client connection

    Requests are ingested and enqueued with the manager."""

    @property
    def manager(self):
        assert isinstance(self.server, Server)
        return self.server.manager

    def handle(self):
        logger.debug("New connection")
        req = ''
        while True:
            req += str(self.request.recv(1024), 'utf-8')

            if len(req) == 0:
                logger.debug("Disconnected")
                self.request = None
                return

            try:
                msg = proto.Message.deserialize(req)
                req = ''
            except proto.MessageParseError as exc:
                logger.debug("Not (yet?) valid request '%s': %s", req, exc)
                msg = None
            except proto.InvalidMessageError as exc:
                logger.info("Invalid message: %s", req)
                self.request = None
                return

            if msg is not None:
                self.manager.requests.put((self, msg.copy()))

    def send(self, msg):
        """Send 'msg'

        This call posts the sending in a separate thread and returns immediately
        """
        threading.Thread(target=self.do_send, args=(msg,)).start()

    def do_send(self, msg):
        """Actually send 'msg' to the connected client"""
        try:
            self.wfile.write(bytes(msg.serialize(), 'utf-8'))
        except OSError as exc:
            logger.info("Could not send response: %s", exc)

    def err(self, reason=None):
        """Send an error response"""
        self.send(proto.ErrorResponse(reason=reason))

    def ok(self):
        """Send an 'ok' response"""
        self.send(proto.OkayResponse())


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    def __init__(self, manager):
        socketpath = manager.config.path(configuration.SECTION_GENERAL,
                                         configuration.CONFIG_SOCKET)
        super().__init__(str(socketpath), ConnectionHandler)
        self.path = socketpath
        self.manager = manager
        self.manager.server_process = self

    def cleanup(self):
        try:
            self.path.unlink()
        except OSError as exc:
            logger.error("Could not remove %s: %s", self.path, exc)


class Manager:
    def __init__(self, config):
        self.config = config
        self.dbpath = config.path(configuration.SECTION_GENERAL,
                                  configuration.CONFIG_CACHE) / "db"

        self.dbconn = None
        self._qparser = None

        self.server_process = None

        # xapian prefixes are upper-case strings consisting only of letters
        # and starting with X for user-defined prefixes
        # the mapping of human-readable to xapian prefixes is here:
        self.prefixpath = configuration.CACHEPATH / "prefixes.csv"
        self.human_to_prefix = {}
        self.prefix_to_human = {}
        # indexers produce their own tags (e.g. 'epub.writer'), but for
        # indexing they need to map to one of the base-level tags (e.g. 'author')
        self.tag_mapping = {}

        self.load_prefix_translations()
        self.load_tag_mapping()

        self.requests = queue.Queue(20)
        self.thread = None

        self.stemmers = {lang: xapian.Stem(lang)
                         for lang in ["en", "sv", "de"]}

    def load_tag_mapping(self):
        self.tag_mapping = {}
        updated = False

        for tag in self.config[configuration.SECTION_SYNONYMS]:
            self.tag_mapping.update({s: tag
                                     for s in self.config.list(configuration.SECTION_SYNONYMS,
                                                               tag)})

        for tag in self.config[configuration.SECTION_SYNONYMS]:
            if tag in self.human_to_prefix or tag in BASE_TAGS:
                continue
            prefix = next_prefix(self.prefix_to_human.keys())

            self.human_to_prefix[tag] = prefix
            self.prefix_to_human[prefix] = tag
            logger.debug("Added %s -> %s mapping", tag, prefix)
            updated = True

        if updated:
            self.save_prefix_translations()

    def load_prefix_translations(self):
        """Load the translations of tag->xapian prefix from disk"""
        if not self.prefixpath.is_file():
            return

        with open(self.prefixpath, 'rt', newline='', encoding='utf-8') as prefixfile:
            reader = csv.reader(prefixfile)
            self.human_to_prefix = {line[0]: line[1] for line in reader}
        self.prefix_to_human = {value: key
                                for key, value in self.human_to_prefix.items()}
        # reset the queryparser to enforce reloading of the translations
        self._qparser = None

    def save_prefix_translations(self):
        """Save the translations of tag->xapian prefix to disk"""
        with open(self.prefixpath, 'wt', newline='', encoding='utf-8') as prefixfile:
            writer = csv.writer(prefixfile)
            writer.writerows([[title, prefix]
                              for title, prefix in sorted(self.human_to_prefix.items())])

    def ensure_connection(self):
        """Ensure that the xapian database connection is established and "fresh".

        Returns 'False' if no database connection could be established.
        """
        if self.dbconn is None:
            try:
                self.dbconn = xapian.Database(str(self.dbpath))
            except xapian.DatabaseNotFoundError as exc:
                logger.debug("Read connection failed: %s", exc)
                return False

        self.dbconn.reopen()
        return True

    def start(self):
        """Start the blocking 'wait_for_requests' in a new thread"""
        self.thread = threading.Thread(target=self.wait_for_requests)
        self.thread.start()

    def stop(self):
        """Stop the wait_for_requests thread, if it is running"""
        if self.thread is None:
            return
        self.requests.put((None, None))
        self.thread.join()
        self.thread = None

    def wait_for_requests(self):
        """Wait for new requests

        This is blocking"""
        while True:
            client, msg = self.requests.get()

            if client is None:
                break

            self.handle_request(client, msg)

    def handle_request(self, client, msg):
        """Handle the proto.Message 'msg' from 'client'

        Only one request will be handled at a time"""
        if isinstance(msg, proto.Ping):
            client.send(proto.Pong())

        elif isinstance(msg, proto.Update):
            if self.update(msg.entries):
                client.ok()
            else:
                client.err()

        elif isinstance(msg, proto.Query):
            try:
                results = self.search(msg.query)
                client.send(proto.QueryResult(results=results))
            except RuntimeError as exc:
                client.err(str(exc))

        elif isinstance(msg, proto.GetMetadata):
            results = self.get_metadata(msg.paths)
            if msg.selected_tags is not None:
                results = [[id_, filter_tags(r, msg.selected_tags)]
                           for id_, r in results]
            client.send(proto.QueryResult(results=results))

        elif isinstance(msg, proto.Clear):
            if self.clear():
                client.ok()
            else:
                client.err()

        elif isinstance(msg, proto.Forget):
            self.forget(msg.paths)
            client.ok()

        elif isinstance(msg, proto.GetMostRecent):
            entry = self.get_most_recent()
            if entry is None:
                client.send(proto.QueryResult(results=[]))
            else:
                client.send(proto.QueryResult(results=[entry]))

        elif isinstance(msg, proto.GetConfig):
            client.send(proto.Config(config=self.config))

        elif isinstance(msg, proto.Shutdown):
            client.ok()
            threading.Thread(target=self.stop_server_process).start()

        elif isinstance(msg, proto.Compact):
            if self.compact():
                client.ok()
            else:
                client.err()

        else:
            client.err("Unknown command")

    def unique(self, path):
        """Create a unique identifier for the given path"""
        # TODO - this should also include the block device identifier and hostname
        # on which the file is found
        text = str(path)
        hashedpath = hashlib.sha1(bytes(text, 'utf-8')).hexdigest()
        return hashedpath

    def update(self, entries):
        """Update the CacheEntry 'entry' in the database

        Returns 'True' on success, otherwise 'False'
        """
        db_exists = self.ensure_connection()

        dbconn = xapian.WritableDatabase(str(self.dbpath))
        indexer = xapian.TermGenerator()

        dbconn.begin_transaction()
        for entry in entries:
            # build a unique identifier for the given entry
            strpath = str(entry.path)
            pathid = self.unique(entry.path)

            # attempt to find the document to see if it needs to be replaced instead of added
            docid = None
            if db_exists:
                enquire = xapian.Enquire(self.dbconn)
                query = xapian.QueryParser()
                query.set_database(self.dbconn)
                query = query.parse_query(pathid, xapian.QueryParser.FLAG_DEFAULT, ID_PREFIX)
                enquire.set_query(query)

                matches = [m.docid for m in enquire.get_mset(0, 5)]
                if len(matches) > 0:
                    docid = matches[0]
                    logger.debug("Updating document instead of creating a new one for %s",
                                 entry.path)

                del enquire
                del query

            language = entry.get('language')
            if len(language) == 0:
                language = 'en'
            else:
                language = language[0].raw_value

            doc = xapian.Document()
            indexer.set_document(doc)
            indexer.set_stemmer(self.stemmers.get(language, self.stemmers['en']))

            keys = {}
            # all indexable keys, their prefix, and whether any humanizable values exist
            for key, values in entry.metadata.items():
                key = self.config.synonymized.get(key, key)
                key = self.tag_mapping.get(key, key)
                prefix = BASE_TAGS.get(key, self.human_to_prefix.get(key, None))

                if prefix is None:
                    continue

                if key not in keys:
                    keys[key] = (prefix, [])
                keys[key][1].extend(values)

            # first index the raw values, but already collect humanized values
            humanized = []
            for key, pair in keys.items():
                indexer.increase_termpos(50)
                prefix, values = pair

                lhuman = []
                for value in values:
                    indexer.index_text(str(value.raw_value), 1, prefix)
                    logger.debug("... indexing %s", value.raw_value)
                    if value.humanized_value is not None:
                        lhuman.append(value.humanized_value)

                if len(lhuman) > 0:
                    humanized.append((prefix, lhuman))

                if len(prefix) == 0 or key not in self.config.implicit_tags:
                    continue

                indexer.increase_termpos(50)

                for value in values:
                    indexer.index_text(str(value.raw_value))

            for prefix, values in humanized:
                indexer.increase_termpos(50)

                for value in values:
                    indexer.index_text(value)

            if 'filename' in self.config.implicit_tags:
                indexer.index_text(entry.path.stem)

            doc.set_data(json.dumps(entry.as_dict()))

            doc.add_value(SLOT_FILEPATH, strpath)
            doc.add_value(SLOT_LASTMODIFIED, entry.last_modified.strftime(shared.TIMESTAMP_FORMAT))
            doc.add_boolean_term(ID_PREFIX + pathid)
            if entry.storage_label is not None:
                doc.add_term(BASE_TAGS['storage'] + str(entry.storage_label))
            if entry.rel_path is None:
                doc.add_term(BASE_TAGS['rel_path'] + strpath)
            else:
                doc.add_term(BASE_TAGS['rel_path'] + str(entry.rel_path))
            if entry.mimetype is not None:
                doc.add_term(BASE_TAGS['mime'] + entry.mimetype)
            doc.add_term(BASE_TAGS['path'] + str(entry.path.parent))
            doc.add_term(BASE_TAGS['file'] + str(entry.path.stem))

            suffix = entry.path.suffix
            if suffix.startswith('.'):
                suffix = suffix[1:]
            doc.add_term(BASE_TAGS['extension'] + suffix)

            if docid is None:
                dbconn.add_document(doc)
            else:
                dbconn.replace_document(docid, doc)

        dbconn.commit_transaction()
        dbconn.close()
        return True

    def clear(self):
        """Clear the databasee"""
        if not self.ensure_connection():
            raise RuntimeError("Could not connect to database")
        logger.info("Flushing database")
        docids = [d.docid for d in self.dbconn.postlist("")]

        self.delete_documents(docids)

        return True

    def forget(self, paths):
        """Remove knowledge about these paths from the database"""
        docids = set()
        for doc in self.iter_paths(paths):
            docids.add(doc.docid)

        self.delete_documents(docids)

    def get_most_recent(self):
        """Get the entry with the most recent last_modified"""
        if not self.ensure_connection():
            raise RuntimeError("Could not connect to database")
        most_recent = CacheEntry(None).as_dict()
        keep_id = None

        docids = {d.docid for d in self.dbconn.postlist("")}
        for docid in docids:
            doc = self.dbconn.get_document(docid)
            timestamp = str(doc.get_value(SLOT_LASTMODIFIED), 'ascii')
            if timestamp > most_recent['last_modified']:
                most_recent = json.loads(str(doc.get_data(), 'utf-8'))
                keep_id = docid

        return [keep_id, most_recent]

    def delete_documents(self, docids):
        """Delete the documents with the given IDs"""
        dbconn = xapian.WritableDatabase(str(self.dbpath))
        dbconn.begin_transaction()
        for docid in docids:
            dbconn.delete_document(docid)
        dbconn.commit_transaction()
        dbconn.close()

    def queryparser(self):
        """Return the queryparser"""
        if self._qparser is None:
            self._qparser = xapian.QueryParser()
            # self._qparser.set_stemmer(self.stemmers['en'])

            all_tags = BASE_TAGS.copy()
            all_tags.update(self.human_to_prefix)

            for human, prefix in all_tags.items():
                self._qparser.add_prefix(human, prefix)

        self._qparser.set_database(self.dbconn)
        return self._qparser

    def enquire(self, query):
        """Create a new Enquire session with the given query"""
        enquire = xapian.Enquire(self.dbconn)
        query = self.queryparser().parse_query(query)
        enquire.set_query(query)
        return enquire

    def search(self, querytext):
        """Search the database with the given query

        Returns a list of CacheEntries matching the search
        """
        if not self.ensure_connection():
            raise RuntimeError("Could not connect to database")

        if len(querytext.strip()) == 0:
            matches = {d.docid for d in self.dbconn.postlist("")}
            matches = [[m, json.loads(str(self.dbconn.get_document(m).get_data(), 'utf-8'))]
                       for m in matches]
            return matches

        enquire = self.enquire(querytext)

        matches = []
        more_matches = True
        while more_matches:
            imatches = enquire.get_mset(len(matches), len(matches)+10)
            if imatches.size() < 10:
                more_matches = False
            for match in imatches:
                if match.percent < 50:
                    more_matches = False
                    break
                matches.append([match.docid, json.loads(str(match.document.get_data(), 'utf-8'))])

        return matches

    def get_metadata(self, paths):
        results = []
        for doc in self.iter_paths(paths):
            document = json.loads(str(doc.document.get_data(), 'utf-8'))
            results.append([doc.docid, document])
        return results

    def iter_paths(self, paths):
        """Iterate through the documents given by these paths"""
        if not self.ensure_connection():
            raise RuntimeError("Could not connect to database")

        enquire = xapian.Enquire(self.dbconn)
        queryparser = xapian.QueryParser()
        queryparser.set_database(self.dbconn)

        for path in paths:
            query = queryparser.parse_query(str(path),
                                            xapian.QueryParser.FLAG_DEFAULT,
                                            BASE_TAGS['rel_path'])
            enquire.set_query(query)

            matchcount = 0
            more_matches = True
            while more_matches:
                matches = enquire.get_mset(matchcount, matchcount+5)

                if matches.size() < 5:
                    more_matches = False

                for match in matches:
                    yield match

    def stop_server_process(self, *_):
        logger.debug("Stop server process requested")
        if self.server_process is None:
            logger.debug("Server process not running")
            return

        logger.debug("Shutting down")
        self.server_process.shutdown()
        self.server_process = None

    def compact(self):
        logger.info("Compacting database")

        # disconnect
        logger.debug(" ... closing current connection")
        if self.dbconn is not None:
            self.qparser = None
            self.dbconn.close()
            self.dbconn = None

        # delete any existing backed-up database
        backuppath = self.dbpath.parent / "db.bak"
        if backuppath.is_dir():
            logger.debug(" ... cleaning up earlier backup")
            try:
                shutil.rmtree(backuppath)
            except OSError as exc:
                logger.error("Could not clean away previous backup: %s", exc)
                return False

        # make the current database the backup
        logger.debug(" ... rename current database to 'backup'")
        try:
            self.dbpath.rename(backuppath)
        except OSError as exc:
            logger.error("Failed to rename the database: %s", exc)
            return False

        # calculate the size of the database
        pre_compact_size = sum([file_.stat().st_size
                                for file_ in backuppath.iterdir()
                                if file_.is_file()])

        # compact the backup into the self.dbpath location
        try:
            conn = xapian.Database(str(backuppath))
            conn.reopen()
        except xapian.DatabaseNotFoundError as exc:
            logger.error("Could not open the backup after copying: %s", exc)
            return False

        logger.debug(" ... compacting")
        conn.compact(str(self.dbpath))

        # calculate the size of the compacted database
        post_compact_size = sum([file_.stat().st_size
                                 for file_ in backuppath.iterdir()
                                 if file_.is_file()])
        
        pre_size = round(pre_compact_size / 1048576.0, 2)
        post_size = round(post_compact_size / 1048576.0, 2)

        logger.info(f"Compacted from {pre_size} MB to {post_size} MB")

        # delete the backup
        logger.debug(" ... deleting the backup")
        try:
            shutil.rmtree(backuppath)
        except OSError as exc:
            logger.warning("Could not delete the backup of the database: %s", exc)

        return True


def filter_tags(result, selected_tags):
    if selected_tags is None:
        return result

    if isinstance(selected_tags, list):
        selected_tags = set(selected_tags)

    filtered = {'path': result['path']}

    if len(selected_tags) == 0:
        return filtered

    if 'last_modified' in selected_tags:
        filtered['last_modified'] = result['last_modified']

    if selected_tags == {'last_modified'}:
        return filtered

    filtered['metadata'] = {k: v for k, v in result['metadata'].items()
                            if k in selected_tags}

    return filtered


def next_prefix(known):
    indices = [0]
    letters = string.ascii_uppercase
    while True:
        prefix = 'X' + ''.join([letters[p] for p in indices])
        if prefix not in known:
            return prefix

        overflow = True
        for pos in range(len(indices)-1, -1, -1):
            if indices[pos] + 1 < len(letters):
                indices[pos] += 1
                for other in range(pos+1, len(indices)):
                    indices[other] = 0
                overflow = False
                break

        if overflow:
            indices = [0]*(len(indices) + 1)


def is_server_running(config):
    from metaindex.client import Client
    client = Client(config)
    other_server_running = client.connection_ok()

    return other_server_running


def stop_running_server(config):
    from metaindex.client import Client
    client = Client(config)

    if not client.connection_ok():
        return

    client.send(proto.Shutdown())
    client.recv()


def launch(config):
    manager = Manager(config)
    manager.start()

    with Server(manager) as server:
        try:
            server.serve_forever()
        except (KeyboardInterrupt, EOFError):
            pass

    manager.stop()
    manager.save_prefix_translations()
    server.cleanup()


def daemonize(config):
    """Launch the server as a daemon"""

    try:
        pid = os.fork()
        if pid > 0:
            return True
    except OSError:
        return False

    os.chdir('/')
    os.setsid()
    os.umask(0)

    if os.fork() > 0:
        return True

    sys.stdout.flush()
    sys.stderr.flush()

    sys.stdin.close()
    sys.stdout.close()
    sys.stderr.close()

    if not logger.is_set_up():
        logger.setup(level=config.get(configuration.SECTION_SERVER, configuration.CONFIG_LOGLEVEL).upper(),
                     filename=config.get(configuration.SECTION_SERVER, configuration.CONFIG_LOGFILE))
    launch(config)


def run():
    args = parse_args()

    config = configuration.load(args.config)
    if not args.stop and is_server_running(config):
        logger.info("Another server is already running")
        return 1

    loglevel = args.log_level or config.get(configuration.SECTION_SERVER, configuration.CONFIG_LOGLEVEL)
    logfile = args.log_file or config.get(configuration.SECTION_SERVER, configuration.CONFIG_LOGFILE)

    logger.setup(level=loglevel.upper(), filename=logfile)

    if args.stop:
        stop_running_server(config)
    elif args.detach:
        daemonize(config)
    else:
        launch(config)

    return 0


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config',
                        default=None,
                        type=str,
                        help="Location of the configuration file. Defaults to " \
                             + str(configuration.CONFIGFILE))

    parser.add_argument('-l', '--log-level',
                        default=None,
                        choices=['debug', 'info', 'warning', 'error', 'fatal'],
                        help="The level of logging. Defaults to %(default)s.")
    parser.add_argument('--log-file',
                        default=None,
                        type=str,
                        help="Write log information to this file instead of stderr.")
    parser.add_argument('-d', '--detach',
                        default=False,
                        action='store_true',
                        help="Detach from command line and run the server in the background.")
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s ' + version.__version__)
    parser.add_argument('-s', '--stop',
                        default=False,
                        action='store_true',
                        help='Instead of starting a server, shut down a running server')

    return parser.parse_args()


if __name__ == '__main__':
    run()
