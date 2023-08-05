"""Functions, names, and identifiers shared in the code"""
import codecs
import datetime
from pathlib import Path

EXTRA = 'extra.'
IS_RECURSIVE = 'extra_metadata_is_recursive'
LAST_MODIFIED = 'extra_metadata_last_modified'
TIMESTAMP_FORMAT = "%Y%m%dT%H%M%S"

DUBLINCORE_TAGS = {
    'contributor',
    'coverage',
    'creator',
    'date',
    'description',
    'format',
    'identifier',
    'language',
    'publisher',
    'relation',
    'rights',
    'source',
    'subject',
    'title',
    'type',
}


def get_last_modified(file_):
    """Return the last_modified datetime of the given file.

    This will drop the microsecond part of the timestamp! The reasoning is that
    last_modified will be taken during database cache updates. If a change
    happens at the same second to a file, just after the indexer passed it,
    there's probably a good chance the file gets modified again in the near
    future at which point the indexer will pick up the change.
    Other than that, the cache can forcefully be cleared, too.
    """
    return datetime.datetime.fromtimestamp(file_.stat().st_mtime).replace(microsecond=0)


def strfdt(timestamp):
    """Return the strftime'd timestamp

    This function will also ensure that the returned value has the correct
    amount of leading zeroes, for example when the datetime should be 0001-01-01.
    """
    text = timestamp.strftime(TIMESTAMP_FORMAT)
    return "0"*max(0, 15-len(text)) + text


def strpdt(text):
    return datetime.datetime.strptime(text, TIMESTAMP_FORMAT)


def find_files(paths, recursive=True, ignore_dirs=None):
    """Find all files in these paths"""
    if not isinstance(paths, list):
        paths = [paths]
    if ignore_dirs is None:
        ignore_dirs = []

    pathqueue = list(paths)
    filenames = []

    while len(pathqueue) > 0:
        path = pathqueue.pop(0)

        if not isinstance(path, Path):
            path = Path(path)

        if not path.exists():
            continue

        for item in path.iterdir():
            if item.is_dir() and recursive and item.parts[-1] not in ignore_dirs:
                pathqueue.append(item)
                continue

            if item.is_file():
                filenames.append(item)

    return filenames


def make_mount_relative(path):
    """Return the path relative to its mount point

    For example, a file ``/mnt/EXTHD/doc.pdf`` would return ``/doc.pdf``
    if ``/mnt/EXTHD`` is the mount point.
    """
    path = path.resolve()
    devid = path.stat().st_dev

    # not a mount point at all
    if Path(path.parts[0]).stat().st_dev == devid:
        return path

    parts = [path.name]
    path = path.parent

    while path.parent != path and path.stat().st_dev == devid:
        parts.insert(0, path.name)
        path = path.parent

    # The 'root' of the mount point, eg. 'EXTHD' should not be
    # part of the relative path
    path = Path(*(parts[1:]))
    return path


def jsonify(that):
    """Return ``that`` in a form that can be exported as JSON"""
    if isinstance(that, datetime.datetime):
        return strfdt(that)

    if isinstance(that, datetime.date):
        text = that.strftime("%Y%m%d")
        return "0"*(max(0, 8-len(text)))+text

    if isinstance(that, (tuple, set)):
        return list(that)

    if isinstance(that, Path):
        return str(that)

    return that


def to_utf8(raw):
    """Decode a blob of bytes into a UTF-8 string
    
    Attempts to determine the encoding automatically
    """
    if isinstance(raw, str):
        return raw
    encoding = None
    skip = 1

    if raw.startswith(codecs.BOM_UTF8):
        encoding = 'utf-8'
    elif raw.startswith(codecs.BOM_UTF16_BE):
        encoding = 'utf-16-be'
    elif raw.startswith(codecs.BOM_UTF16_LE):
        encoding = 'utf-16-le'
    elif raw.startswith(codecs.BOM_UTF32_BE):
        encoding = 'utf-32-be'
    elif raw.startswith(codecs.BOM_UTF32_LE):
        encoding = 'utf-32-le'
    else:
        # just best efford
        encoding = 'utf-8'
        skip = 0

    try:
        text = str(raw, encoding=encoding).strip()
        return text[skip:]  # drop the BOM, if applicable
    except UnicodeError:
        pass
    return None
