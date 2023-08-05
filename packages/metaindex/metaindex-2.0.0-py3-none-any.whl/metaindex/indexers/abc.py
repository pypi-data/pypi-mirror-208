"""abc notation file indexer"""
import re

from metaindex import logger
from metaindex.indexer import IndexerBase, only_if_changed


class ABCNotationIndexer(IndexerBase):
    """Indexer for abc music notation files"""
    NAME = 'abcnotation'
    ACCEPT = ['text/vnd.abc', '.abc']
    PREFIX = ('abc',)

    INFO_MAPPING = {
        't': 'title',
        'm': 'meter',
        'c': 'composer',
        'd': 'discography',
        'z': 'transcription',
        'g': 'group',
        'r': 'rhythm',
        'k': 'key',
        'o': 'origin',
    }
    INFO_RE = re.compile(r'^([a-zA-Z]):(.*)$')

    @only_if_changed
    def run(self, path, metadata, _):
        logger.debug("[%s] processing %s", self.NAME, path.name)

        with open(path, 'rt', encoding="utf-8") as filehandle:
            lines = []

            # pre-filter lines by dropping comments and joining lines
            for line in filehandle:
                line = line.lstrip()
                if line.startswith('%'):
                    continue
                line = self.strip_comment(line)
                if line.startswith('+') and len(lines) > 0 and lines[-1][1] == ':':
                    lines[-1] += line[1:]
                lines.append(line)

            for line in lines:
                match_ = self.INFO_RE.match(line)

                if match_ is not None:
                    fieldinfo = self.INFO_MAPPING.get(match_.group(1).lower(), None)
                    if fieldinfo is not None:
                        metadata.add('abc.' + fieldinfo,
                                     match_.group(2).strip())

    @staticmethod
    def strip_comment(line):
        """Parse an information field

        Strip comments if there are any
        """
        result = ""
        prevletter = None
        for letter in line:
            if letter == '%' and prevletter != '\\':
                break
            prevletter = letter
            result += letter
        return result
