Index some directories
~~~~~~~~~~~~~~~~~~~~~~

To index you ``Documents`` and ``Pictures`` folder recursively::

  metaindex index -r ~/Documents ~/Pictures


Find all files
~~~~~~~~~~~~~~

List all files that are in cache::

  metaindex find


Find file by mimetype
~~~~~~~~~~~~~~~~~~~~~

Searching for all ``image/*`` mimetypes can be accomplished by this::

  metaindex find mimetype:image/


Listing metadata
~~~~~~~~~~~~~~~~

To list all metadata tags and values of all image files::

  metaindex find -t -- "ext:odt$"

List the resolutions of all files that have the ``resolution`` metadata tag::

  metaindex find -t resolution -- "resolution?"

