"""generate: static site file generation

This is the processing and output stage of the dirt SSG.
Generated files and directories go into an output directory (default: public/)
that is protected by a lock file created before generating and removed after.
For update purposes, the directory also has a timestamp file that contains
the date/time that the most recent generation pass happened -- this also
serves as a version number for the site that guides automatic page refresh.

Composition of pages for a specific framework is handled in the composer.
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


from dirt.common import DirtError, PAGE_EXTENSION, site_url
from dirt.conversion import Markdown2Html
from dirt.htmlify import BuildHtml
from dirt.pageinfo import PageInfo

from datetime import datetime
import os
import re
import shutil
from typing import Tuple, Dict

LOCK_FILENAME = ".LOCK.dirt"
TIMESTAMP_FILENAME = ".TIMESTAMP.dirt"

markdown_engine = Markdown2Html()


def generate_start(destinationdir):
    """Start generation by locking the public/ directory first.
    Returns the new timestamp if generation can proceed, or None if locked.
    """
    timestamp = datetime.utcnow().isoformat()
    lock_path = os.path.join(destinationdir, LOCK_FILENAME)
    if (os.path.exists(lock_path)):
        return None
    with open(lock_path, 'w') as f:
        f.write(timestamp)
    if (os.path.exists(lock_path)):
        return timestamp
    return None


def generate_done(destinationdir):
    """Done with generation so unlock the public/ directory first.
    Returns whether the unlock happened properly or not.
    """
    lock_path = os.path.join(destinationdir, LOCK_FILENAME)
    timestamp_path = os.path.join(destinationdir, TIMESTAMP_FILENAME)
    if (os.path.exists(lock_path)):
        # double-check to prevent disaster
        if (lock_path.startswith(str(destinationdir))):
            if (lock_path[-5:] == ".dirt"):
                try:
                    shutil.move(lock_path, timestamp_path)
                    return True
                except FileNotFoundError:
                    return False
    return False


def load_page(ext, frompath, destinationdir, rootreldir, basename,
              verbose=False) -> PageInfo:
    """Load content page meta data, convert to HTML as phase one of making it.
    Returns page object that make_page will consume later to generate it.
    """
    if (ext != "md"):
        raise DirtError("Unsupported content file extension: %s" % ext)
    metadata, mdhtml = load_markdown(frompath)
    metadata['filename'] = basename
    if ('date' not in metadata):
        modtime = os.path.getmtime(frompath)
        dt = datetime.fromtimestamp(modtime)
        metadata['date'] = dt.strftime('%Y-%m-%d %H:%M:%S')
    links = collect_links(mdhtml)
    url = site_url(os.path.join(rootreldir, basename + PAGE_EXTENSION))
    filepath = os.path.join(destinationdir, basename) + PAGE_EXTENSION
    return PageInfo(metadata=metadata, mdhtml=mdhtml,
                    url=url, filepath=filepath, links=links)


def make_page(cxt, page, verbose=False):
    """After ordering, compose and write the generated page.
    """
    composer = cxt.site['framework']
    pagehtml = composer.compose(page.mdhtml, page.metadata)
    with open(page.filepath, 'w') as f:
        f.write(pagehtml)


def load_markdown(mdpath: str) -> Tuple[Dict[str, str], str]:
    """Load markdown file and convert to HTML, used for headers/footers.
    Metadata at the front of markdown comes as {'key': ["value"]}
    which we convert to just {'key': 'value'}. Return as HTML fragment.
    """
    try:
        with open(mdpath, 'r') as f:
            mdtext = f.read()
            html = markdown_engine.convert(mdtext)
            mdmetadata = markdown_engine.metadata()
            metadata = dict()
            for key in mdmetadata:
                metadata[key] = mdmetadata[key][0]
            return metadata, html
    except FileNotFoundError:
        pass
    raise DirtError("Cannot open markdown file: " + mdpath)


def collect_links(html):
    """Returns a list of links found in the html.
    TODO: should be proper HTML parse ideally
    """
    links = list()
    for m in re.finditer(r'''href=['"]([^'"]+)['"]''', html, re.IGNORECASE):
        url = m.group(1)
        if (url[0] != '#'):
            links.append(url)
    return links


def addon_script(cxt, interval=1):
    """Build and return addon script HTML fragment used for auto-update.
    """
    current_timestamp = cxt.timestamp
    template = cxt.snippets['local_jscript']
    script = BuildHtml(template)
    script.insert('extraslink', cxt.snippets['_extras_link'])
    script.text('timestamp', current_timestamp)
    script.text('filename', TIMESTAMP_FILENAME)
    script.text('interval', str(interval))
    return script.render()


def soft_copyfile(sourcepath, destinationpath):
    """Copy file from source to destination unless it exists and no change.
    If the destination exists we check modification date is >= source file's.
    """
    if (os.path.isfile(destinationpath)):
        dest_mod = os.path.getmtime(destinationpath)
        source_mod = os.path.getmtime(sourcepath)
        if (dest_mod > source_mod):
            return False
    os.makedirs(os.path.dirname(destinationpath), exist_ok=True)
    shutil.copyfile(sourcepath, destinationpath)
    return True
