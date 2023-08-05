"""Convenience access to ElementTree as etree

Various places in metaindexer use XML; this is a good place to get the
``etree`` class from and before use call ``check_defusedxml`` to inform the
user about a potentially missing ``defusedxml`` dependency.
"""
try:
    import defusedxml
    from defusedxml import ElementTree as etree
except ImportError:
    defusedxml = None
    from xml.etree import ElementTree as etree

from metaindex import logger


def check_defusedxml():
    """Check the use of defusedxml"""
    global defusedxml
    if defusedxml is None:
        logger.warning("You are using the unsafe XML parser from python. "
                       "Please consider installing 'defusedxml'.")
        defusedxml = False
