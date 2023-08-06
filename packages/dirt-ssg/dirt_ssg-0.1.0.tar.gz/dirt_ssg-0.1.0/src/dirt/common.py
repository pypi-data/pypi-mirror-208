"""common: common code for dirt SSG
Standard file and path names; error exception class; path constructor.
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


import os
import re


META_DIR = "./meta/"          # meta/ folder contains bundled files
CONFIG_TOML = "_config.toml"  # content directory configuration file
DIRT_TOML = "dirt.toml"       # default dirt configuration file
INDEX_FILE = "index"          # name of the root file in a site directory
PAGE_EXTENSION = ".html"      # standard generated HTML file extension
EXTRAS_DIR = "_explore"       # name of extras directory for local browsing


class DirtError(Exception):
    def __init__(self, message):
        self.message = message


def dirt_dir(path):
    """Returns file path for dirt-relative path."""
    dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            '../..', path)
    dir_path = os.path.normpath(dir_path)
    if (os.path.isdir(dir_path)):
        return dir_path
    raise DirtError("No such directory: %s" % path)


def canonical_rel(path, dot=True):
    """Returns the canonical relative form of path.
    The purpose of this is to canonicalize the forms "./dir" and "dir".
    The dot parameter specifies that "./dir" is canonical, or False
    means that "dir" is. The canonical relative root is always ".".
    """
    relpath = os.path.relpath(path)
    if (dot and relpath != "."):
        return "./" + relpath
    else:
        return relpath


def site_url(path):
    """Returns absolute URL for a path in the website.
    This resolves ambiguity of "a/b.html" and "/a/b.html" to the latter form.
    """
    if (path.startswith("./")):
        url = path[1:]
    elif (path == "."):
        url = "/"
    elif (path[0] == '/'):
        url = path
    else:
        url = "/" + path
    return url


def ignore_file(filename):
    """Returns whether to ignore this file by name. This matches commonly used
    temporary and backup files that may be in the source content directory.
    # TODO better way should exist; this is just trial and error
    """
    if (re.match(r'^#[^#]+#$', filename)):
        return True
    if (filename.endswith('~') or filename.startswith('.#')):
        return True
    return False


def boolean_string(value):
    """Returns reasonable boolean interpretation of a string.
    Anything but a few forms of True is considered to be False.
    """
    return value.lower() in ['true', 't', '1', 'y', 'yes']
