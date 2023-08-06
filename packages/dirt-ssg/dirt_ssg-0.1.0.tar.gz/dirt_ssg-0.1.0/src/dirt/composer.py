"""composer: page composer for a dirt simple static site generator library

This module provides different web framework skeletons and renders them.
NOTE: Frameworks must be imported (in config.py) in order to be found by name.
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


from dirt.common import DirtError, dirt_dir, META_DIR, canonical_rel
from dirt.dirtcontext import DirtContext
from dirt.generate import soft_copyfile
from dirt.htmlify import htmltag, htmllink
from dirt.words import curly_expander, excerpt

import os
import re


class DirtFramework():
    """Abstract class for rendering HTML for a specific web framework for dirt.
    """
    def __init__(self, cxt: DirtContext):
        """Initialize instance of a web framework with the site context."""
        self.cxt = cxt

    def __repr__(self):
        return "[DirtFramework: %s]" % self.nickname()

    def nickname(self):
        return nickname_from_class(type(self))

    def setup(self):
        """Setup framework ahead of composing pages.
        Load snippets from files referenced in the dirt config.
        """
        snippets = self.cxt.config.get('snippets', None)
        if (snippets is None):
            return
        for name in snippets:
            snippet = snippets[name]
            self.make_snippet(name, snippet)

    def make_snippet(self, name, snippet):
        """Make a snippet with name and string value.
        String type snippet becomes value or list of one string is a filename,
        files are found in the meta directory.
        """
        if (type(snippet) is str):
            pass
        elif (type(snippet) is list and len(snippet) == 1):
            metapath = dirt_dir(META_DIR)
            filepath = os.path.join(metapath, snippet[0])
            with open(filepath, 'r') as f:
                snippet = f.read()
        else:
            raise DirtError("Invalid [snippets] entry: " + name)
        self.cxt.snippets[name] = snippet

    def add_files(self, realtargetpath):
        """Add files in directory ./meta/frameworks/FXNAME to target directory.
        Returns a dictionary {(relative directory path): [file, name, list]}
        to be used to know what files belong and which should be removed.
        """
        rootpath = dirt_dir(os.path.join(META_DIR,
                                         "frameworks/%s" % self.nickname()))
        added_file_map = dict()
        for dirpath, subdirs, filenames in os.walk(rootpath):
            reldir = canonical_rel(os.path.relpath(dirpath, rootpath),
                                   dot=False)
            generated_filenames = list()
            targetdir = os.path.join(realtargetpath, reldir)
            for filename in filenames:
                relpath = os.path.join(reldir, filename)
                filepath = os.path.join(dirpath, filename)
                destinationpath = os.path.join(realtargetpath, relpath)
                soft_copyfile(filepath, destinationpath)
                generated_filenames.append(filename)
            if (generated_filenames):
                added_file_map[targetdir] = generated_filenames
        return added_file_map

    def page_param(self, meta, param, default=None):
        """Get named parameter from context and return value or default.
        First look in page meta dictionary, then site in context.
        """
        if (param in meta):
            return meta[param]
        rootconfig = self.cxt.site
        return rootconfig.get(param, default)

    def page_title(self, meta: dict) -> str:
        """Compose the text string constituting the page title.
        """
        title = self.page_param(meta, 'title', self.cxt.defaults['title'])
        suffix = self.page_param(meta, 'title_suffix', '')
        if (suffix):
            title += suffix
        return title

    def expansion(self, keyword):
        """Provide HTML expansion of keywords for the framework.
        """
        if (keyword == "menu"):
            if (keyword not in self.cxt.site):
                return None
            site_menu = self.cxt.site[keyword]
            menuhtml = list()
            for key in site_menu:
                url = site_menu[key]
                menuhtml.append(htmllink(key, url))
            return "\n".join(menuhtml)
        return None

    def expand(self, meta, htmltext):
        """Expand {xxx} expressions in HTML generated from markdown.
        """
        def resolver(keyword):
            html = self.expansion(keyword)
            if (html):
                return html
            if (keyword in meta):
                return meta[keyword]
            print(keyword)
            raise DirtError("Invalid substitution: %s" % keyword)
        return curly_expander(htmltext, resolver)

    def inject_previews(self, meta, headtag='h2'):
        """For index pages, inject previews if configured.
        Returns HTML constituting the excerpts, to go after body before footer.
        """
        result = ''
        if (meta['_index']):
            items = self.previews(meta)
            for item in items:
                page = item[0]
                item_title = page.metadata.get('title', ["link"])
                item_html = item[1]
                header = htmltag('a', htmltag(headtag, item_title),
                                 {'href': page.url}).render()
                result += header + '\n' + item_html
        return result

    def previews(self, meta):
        """Collects preview excerpts for the index page:
        these are taken from the first several pages (by ordering)
        of pages in the directory, such as the first lines of blog posts.
        The index page metadata specifies 7 page excerpts or 3 paragraphs by:
        previews: 7
        excerpt: 3
        Returns list of (page, excerpt_html), empty if not configured.
        """
        result = list()
        if ('previews' in meta):
            count = int(meta['previews'])
            if (count > 0):
                paras = int(meta['excerpt']) if ('excerpt' in meta) else 2
                reldir = meta['_dir']
                pages = self.cxt.dirs[reldir].pages
                for page in pages:
                    previewhtml = excerpt(page.mdhtml, maxparas=paras)
                    result.append((page, previewhtml))
                    count = count - 1
                    if (count <= 0):
                        break
        return result

    def page_link(self, page, untitled):
        """Returns HTML link to a page for composing navigation controls.
        If the page has no title, use untitled string instead.
        """
        title = self.page_param(page.metadata, 'title', untitled)
        return htmllink(title, page.url)

    def navigation(self, meta):
        """Returns HTML navigation for pages as 2-ple: (top, bottom).
        """
        navigation = meta.get('_nav', None)
        navtop = ''
        navbottom = ''
        if (navigation):
            prevpage = meta['_prev']
            nextpage = meta['_next']
            nav_html = ''
            sep = '&nbsp;'
            if (prevpage):
                nav_html += self.page_link(prevpage, "Previous⇐") + sep
            if (nextpage):
                nav_html += sep + self.page_link(nextpage, "⇒Next")
            if (navigation == "top"):
                navtop = nav_html
            elif (navigation == "bottom"):
                navbottom = nav_html
        return (navtop, navbottom)

    def compose(self, mdhtml: str, meta: dict) -> str:
        """Compose page and return rendered text. Frameworks must override."""
        return ''


def load_framework(cxt, framework):
    """Framework initialization before SSG generates pages.
    Return valid framework object into the configuration as 'framework'.
    """
    fx_class = find_framework(framework)
    if (fx_class):
        return fx_class(cxt)
    raise DirtError("Unknown framework name: %s" % framework)


def find_framework(framework):
    """Find the specified framework by name from site config.
    Return the framework class for construction, or None if no such framework.
    """
    for fx in DirtFramework.__subclasses__():
        nickname = nickname_from_class(fx)
        if (nickname == framework):
            return fx
    return None


def nickname_from_class(klass):
    """Returns nickname for framework class, usually 'xyz' for XyzFramework.
    """
    classname = klass.__name__
    m = re.search(r'([A-Z][a-z]*)Framework', classname)
    if (m):
        return m.group(1).lower()
    return classname
