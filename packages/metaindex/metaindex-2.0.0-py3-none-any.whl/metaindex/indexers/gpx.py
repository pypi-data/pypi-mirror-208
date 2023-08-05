"""GPX indexer

Native support for GPS Exchange files
"""
import datetime


from metaindex import logger
from metaindex.xmlproxy import etree, check_defusedxml
from metaindex.indexer import IndexerBase


class GPXIndexer(IndexerBase):
    """GPS exchange file indexer"""
    NAME = "gpx"
    ACCEPT = ['.gpx']
    PREFIX = 'gpx'

    ROOT_TAG = 'gpx'

    def run(self, path, metadata, last_cached):
        check_defusedxml()

        tree = etree.parse(path)
        root = tree.getroot()

        if root is None:
            return

        # let's go through all metadata groups in here
        for meta in root.findall('{*}metadata'):
            mapping = [('description', 'desc'),
                       ('name', 'name')]

            for tag, nodename in mapping:
                for node in meta.findall('{*}'+nodename):
                    if node.text is None or len(node.text.strip()) == 0:
                        continue
                    metadata.add(self.PREFIX + '.' + tag, node.text)

            for node in meta.findall('{*}time'):
                if node.text is None:
                    continue
                try:
                    timestamp = datetime.datetime.strptime(node.text[:19],
                                                           '%Y-%m-%dT%H:%M:%S')
                    metadata.add(self.PREFIX + '.time', timestamp)
                except ValueError:
                    pass

            for node in meta.findall('{*}keywords'):
                if node.text is None or len(node.text.strip()) == 0:
                    continue
                for word in node.text.split():
                    if len(word.strip()) > 0:
                        metadata.add(self.PREFIX + '.keyword', word)

            for node in meta.findall('./{*}author/{*}name'):
                if node.text is not None and len(node.text.strip()) > 0:
                    metadata.add(self.PREFIX + '.author', node.text)

            for node in meta.findall('./{*}author/{*}email'):
                localpart = node.attrib.get('id')
                domain = node.attrib.get('domain')
                if None in [localpart, domain]:
                    continue

                metadata.add(self.PREFIX + '.author', f'{localpart}@{domain}')

            for node in meta.findall('./{*}copyright/{*}license'):
                if node.text is None or len(node.text.strip()) == 0:
                    continue
                logger.debug("license: %s", node.text)
                metadata.add(self.PREFIX + '.license', node.text)

            for node in meta.findall('./{*}copyright/{*}year'):
                if node.text is None or len(node.text.strip()) == 0:
                    continue
                logger.debug("copyright year: %s", node.text)
                metadata.add(self.PREFIX + '.copyright', node.text)

            for node in meta.findall('./{*}link'):
                href = node.attrib.get('href')
                if href is None or len(href) == 0:
                    continue
                logger.debug("link: %s", href)
                metadata.add(self.PREFIX + '.link', href)

        wp_counter = 0
        for waypoint in root.findall('{*}wpt'):
            wp_counter += 1
            for node in waypoint.findall('{*}name'):
                if node.text is None or len(node.text.strip()) == 0:
                    continue
                metadata.add(self.PREFIX + '.waypoint.name', node.text)
        if wp_counter > 0:
            metadata.add(self.PREFIX + '.waypoints', wp_counter)

        rt_counter = 0
        for route in root.findall('{*}rte'):
            rt_counter += 1
            for node in route.findall('{*}name'):
                if node.text is None or len(node.text.strip()) == 0:
                    continue
                metadata.add(self.PREFIX + '.route.name', node.text)
        if rt_counter > 0:
            metadata.add(self.PREFIX + '.routes', rt_counter)

        trk_counter = 0
        for track in root.findall('{*}trk'):
            trk_counter += 1
            for node in track.findall('{*}name'):
                if node.text is None or len(node.text.strip()) == 0:
                    continue
                metadata.add(self.PREFIX + '.track.name', node.text)
        if trk_counter > 0:
            metadata.add(self.PREFIX + '.tracks', trk_counter)
