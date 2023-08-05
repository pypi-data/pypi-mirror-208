With metaindex you can find files on your disk based on their metadata, like
the title of a PDF, the keywords of an ebook, or the model of a camera that
a photo was taken with.

The following types of files are supported by default:

 - Images (anything that has EXIF, IPTC, or XMP information),
 - Audio (audio file formats that have ID3 header or similar),
 - Video (most video file formats have an ID3 header),
 - PDF,
 - ebooks (epub natively, calibre metadata files are understood, too).

More file types can be supported through the use of addons.

User provided extra metadata is supported, if it’s provided in the same
directory as the file and the metadata file is ``.metadata.json``.


Server
======

Starting with version ``0.2.0dev0``, requires that the ``metaindexserver``
is running to perform any operations like searching or indexing.

In the default configuration the server will be started automatically as soon
as metaindex needs to connect to the server, but none is running.

However, you may also launch the server process ahead in time like this::

  metaindexserver --detach

It supports a few parameters like ``-c`` to change the configuration file
and ``-l`` to change the log level.

To stop a running server, run ``metaindexserver --stop`` or send it a ``TERM`` signal.


Options
=======

General parameters for ``metaindex`` are:

  ``-c configuration file``
    Use this configuration file instead of the one from the default
    location.

  ``-h``
    Show the help.

  ``-l loglevel``
    Set the level of details shown in logging. Your options are ``fatal``,
    ``error``, ``warning``, ``info``, and ``debug``. Defaults to ``warning``.

  ``--list``
    List all available indexers and exit.

  ``--compact``
    Compact the backend database.

metaindex operates in one of the modes ``index`` or ``find``.

If you want to try the experimental filesystem mode, there is also ``fs``.


Find
----

This is the main operation used to search for files::

  metaindex find [-l directory] [-f [-k]] [-t [tags]] [--] [search queries]

The options to this command are

  ``-t [tags]``
    Metadata tags that you wish to see per found file.

  ``-l directory``
    If this option is provided, metaindex will create this directory (or use
    the existing directory only if it is empty) and create a symbolic link
    to all files that matches this search.

  ``-f``
    Enforce the use of ``-l``’s ``directory``, even if it is not empty.
    Still, metaindex will only work with that directory if it contains only
    symbolic links (e.g. a previous search result)!
    If ``-f`` is provided, all symbolic links in ``directory`` will be
    deleted and the links of this search will be put in place.

  ``-k``
    When you use ``-l`` and ``-f``, ``-k`` will keep all existing links in
    the search directory. That means you can accumulate search results in
    one directory.

  ``search queries``
    The terms to search for. If left empty, all files will be found. See
    below in section search query syntax for the details on search
    queries.
    If the search query is only given as ``-``, metaindex will read the search
    query from stdin.


Index
-----

This is the operation to index files and store that information in the
cache::

  metaindex index [-v[v[v[v]]]] [-C] [-r] paths

The options to this command are

  ``-C``
    Clear the cache. If combined with other options, the flushing of the
    cache will happen first.

  ``-m [paths]``
    Remove missing files. When a file, that's in the index and in the given
    paths, can not be found on disk anymore, it will be removed when this
    option is enabled.
    If ``-m`` is provided, but no paths, all paths in cache will be checked
    for their existence and cleaned up if not found.
    If ``paths`` is ``-``, the list of files will be read from stdin, one
    file per line.
    By default this option is disabled.

  ``-r``
    Run the indexer recursively. That means to visit all files in all
    subdirectories of the paths in the ``-i`` parameter.

  ``-v``
    Make the output more verbose. This option can be provided up to four
    times (``-vvvv``). The steps are:

     * No ``-v``: no output other than errors or information from certain indexers
     * ``-v``: print a ``.`` per file indexed
     * ``-vv``: same as ``-v`` and print how many files were indexed in the end
     * ``-vvv``: same as ``-vv`` but also show how long it took
     * ``-vvvv``: same as ``-vvv`` but print the path of each indexed file instead of just a ``.``

  ``paths``
    Run the indexer on these paths.
    If ``paths`` is ``-``, the list of files will be read from stdin, one
    file per line.


Filesystem (fs)
---------------

On Linux you can try the **experimental** feature of mounting a FuseFS that
will give you a structured access to your files through their metadata::

  metaindex fs [command] [mount point]

The only supported command so far is ``mount``.

It is very experimental and not very useful, but at the same time will not
break any of your files as it only provides a read-only view on your tagged
files.

