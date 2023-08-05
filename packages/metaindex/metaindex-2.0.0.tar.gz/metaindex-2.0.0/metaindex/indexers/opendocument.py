"""OpenDocument indexer

Native support for OpenDocument files, like odt
"""
import datetime
import zipfile

from metaindex import logger
from metaindex.shared import DUBLINCORE_TAGS
from metaindex.xmlproxy import etree, check_defusedxml
from metaindex.indexer import IndexerBase


class OpenDocumentIndexer(IndexerBase):
    """OpenDocument file indexer"""
    NAME = "opendocument"
    ACCEPT = [".odt", "application/vnd.oasis.opendocument.text",
              ".ods", "application/vnd.oasis.opendocument.spreadsheet",
              ".odp", "application/vnd.oasis.opendocument.presentation",
              ".odg", "application/vnd.oasis.opendocument.graphics",
              ".odc", "application/vnd.oasis.opendocument.chart",
              ".odf", "application/vnd.oasis.opendocument.formula",
              ".odi", "application/vnd.oasis.opendocument.image",
              ".odm", "application/vnd.oasis.opendocument.text-master",
              ]
    PREFIX = "opendocument"

    def run(self, path, metadata, last_cached):
        check_defusedxml()

        with zipfile.ZipFile(path, "r") as archive:
            if 'meta.xml' not in archive.namelist():
                logger.debug("No metadata in %s", path)
                return

            xml = archive.read('meta.xml')
            root = etree.fromstring(str(xml, 'utf-8'))
            meta = None
            for node in root.findall('{*}meta'):
                meta = node
                break

            if meta is None:
                logger.debug("Not quite the metadata XML structure as expected in %s",
                             path)
                return

            dctags = DUBLINCORE_TAGS.copy()
            dctags.remove('date')

            for dctag in dctags:
                for node in meta.findall('{*}' + dctag):
                    if node.text is None or len(node.text) == 0:
                        continue
                    metadata.add(self.PREFIX + '.' + dctag, node.text)

            for node in meta.findall('{*}date'):
                if node.text is None or len(node.text) == 0:
                    continue
                try:
                    timestamp = datetime.datetime.strptime(node.text[:19],
                                                           '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    continue
                metadata.add(self.PREFIX + '.date', timestamp)

            for node in meta.findall('{*}keyword'):
                if node.text is None or len(node.text) == 0:
                    continue
                keywords = node.text.split()
                for keyword in keywords:
                    if len(keyword.strip()) == 0:
                        continue
                    metadata.add(self.PREFIX + '.keyword', keyword)
