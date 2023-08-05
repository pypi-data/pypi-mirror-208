import pathlib

from metaindex import shared
from metaindex.cacheentry import CacheEntry
from metaindex.xmlproxy import etree, check_defusedxml


SUFFIX = '.opf'


def get(metadatafile):
    if isinstance(metadatafile, (str, pathlib.Path)):
        with open(metadatafile, "rt", encoding="utf-8") as fh:
            return get(fh)

    entry = parse_opf(metadatafile.read(), shared.EXTRA)
    if hasattr(metadatafile, 'name'):
        entry.path = pathlib.Path(metadatafile.name)

    return entry


def get_for_collection(metadatafile, basepath=None):
    if isinstance(metadatafile, (str, pathlib.Path)):
        with open(metadatafile, "rt", encoding="utf-8") as fh:
            return get_for_collection(fh, pathlib.Path(metadatafile).parent)

    data = parse_opf(metadatafile.read(), prefix=shared.EXTRA)
    data.path = basepath
    data.add(shared.IS_RECURSIVE, True)

    return {basepath: data}


def parse_opf(content, prefix='opf.'):
    check_defusedxml()
    result = CacheEntry(None)

    try:
        root = etree.fromstring(content)
    except:
        return result

    for node in root.findall('.//{http://purl.org/dc/elements/1.1/}*'):
        # tag name will start with {namespace}, get rid of it
        _, tagname = node.tag.split('}', 1)

        tagname = prefix + tagname
        result.add(tagname, node.text)

    for node in root.findall('.//{http://www.idpf.org/2007/opf}meta'):
        _, tagname = node.tag.split('}', 1)

        if 'name' not in node.keys() or 'content' not in node.keys():
            continue

        name = node.get('name')
        if name is not None:
            # calibre specific attributes are just handled as if they were native attributes
            if name.startswith('calibre:'):
                _, name = name.split(':', 1)

            # so far only accept these specific attributes from the IDPF (calibre) namespace
            if name in ['series', 'series_index']:
                result.add(prefix + name, node.get('content'))

    return result
