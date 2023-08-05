"""Office Open XML indexer

Native support for the Office Open XML file format metadata
"""
import datetime
import zipfile

from metaindex import logger
from metaindex.shared import DUBLINCORE_TAGS
from metaindex.xmlproxy import etree, check_defusedxml
from metaindex.indexer import IndexerBase


class OfficeOpenXMLIndexer(IndexerBase):
    """Office Open XML file indexer"""
    NAME = "officeopenxml"
    ACCEPT = ['.docx', '.docm',
              'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
              '.pptx', '.pptm',
              'application/vnd.openxmlformats-officedocument.presentationml.presentation',
              '.xslx', '.xslm',
              'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
              ]
    PREFIX = "officeopenxml"

    def run(self, path, metadata, last_cached):
        check_defusedxml()

        with zipfile.ZipFile(path, "r") as archive:
            if 'docProps/core.xml' not in archive.namelist():
                logger.debug("No metadata in %s", path)
                return

            xml = archive.read('docProps/core.xml')
            root = etree.fromstring(str(xml, 'utf-8'))
            meta = None
            if root.tag.endswith('}coreProperties'):
                meta = root

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

            for kwtag in ['keyword', 'keywords']:
                for node in meta.findall('{*}' + kwtag):
                    if node.text is None or len(node.text) == 0:
                        continue
                    keywords = node.text.split()
                    for keyword in keywords:
                        if len(keyword.strip()) == 0:
                            continue
                        metadata.add(self.PREFIX + '.keyword', keyword)
