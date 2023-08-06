"""extras: extra details to help use the static site builder for dirt SSG
In local server preview, extras display configuration and other state.
TODO: Provide link to staged site version via cxt.snippets['_staged_dir']
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


from dirt.common import INDEX_FILE, PAGE_EXTENSION, EXTRAS_DIR, site_url
from dirt.htmlify import BuildHtml, htmllink
from dirt.urls import Url

import os


def make_extras(cxt):
    """Make extra informational files for local browsing.
    These files are additional info for users to see how the SSG works.
    """
    extras_links = list()
    extras_links.append(site_config_page(cxt))
    items = list()
    page_links = list()
    page_urls = list()
    for dirname in cxt.dirs:
        dirinfo = cxt.dirs[dirname]
        pages = dirinfo.pages
        if (pages):
            directory = BuildHtml('    <h3>$dirname</h3>\n    <p>$summary</p>')
            directory.text('dirname', dirname)
            parameters = (len(pages), "" if len(pages) == 1 else "s",
                          len(dirinfo.statics),
                          "" if len(dirinfo.statics) == 1 else "s")
            summary = "%d page%s; %d static file%s" % parameters
            directory.text('summary', summary)
            items.append(directory.render())
            items.append('    <ul>')
            for page in pages:
                item = BuildHtml('        <li>$link</li>')
                filename = os.path.basename(page.filepath)
                url = page.url
                item.insert('link', htmllink(filename, url))
                items.append(item.render())
                page_urls.append(url)
                for link in page.links:
                    linkurl = Url(link)
                    page_links.append(linkurl.effective(page.url))
            items.append('    </ul>')
    thehtml = '\n'.join(items)
    extras_links.append(extras_page(cxt, 'sitemap', "Site map", thehtml))
    extras_links.append(feeds_page(cxt))
    extras_links.append(links_page(cxt, page_links, page_urls))
    items = list()
    items.append("<ul>")
    for elink in extras_links:
        items.append("  " + elink)
    items.append("</ul>")
    thehtml = "\n      ".join(items)
    cxt.snippets['_extras_link'] = extras_page(cxt, INDEX_FILE,
                                               "summary", thehtml)


def site_config_page(cxt):
    """Make extras site configuration page and return link for the summary.
    """
    items = list()
    items.append("<ul>")
    for param in cxt.site:
        if (param[0] != '_'):
            items.append("  " + line_item(param, cxt.site[param]))
    items.append("</ul>")
    thehtml = "\n      ".join(items)
    return extras_page(cxt, 'config', "Site config", thehtml)


def feeds_page(cxt):
    """Make extras feeds summary page and return link for the summary.
    """
    items = list()
    items.append("<ul>")
    feeds = cxt.site.get('feed', [])
    for feedname in feeds:
        feed = feeds[feedname]
        title = feed.get('title', "(untitled)")
        url = feed.get('_url', "?")
        items.append("  " + line_item(title, url))
    items.append("</ul>")
    thehtml = "\n      ".join(items)
    return extras_page(cxt, 'feeds', "RSS Feeds", thehtml)


def links_page(cxt, page_links, page_urls):
    """Make extras links summary page and return link for the summary.
    2nd parameter is links in website pages (not statics)
    3rd parameter is URLs of website pages (not statics)
    """
    unique_links = set(page_links)  # TODO effective
    items = list()
    summary = BuildHtml('    <p>$summary</p>\n')
    numbers = (len(page_links), len(unique_links), len(page_urls))
    stats = "Total links: %d; unique links: %d; site pages: %d" % numbers
    summary.text('summary', stats)
    items.append(summary.render())
    ext_links = list()
    broken_links = list()
    for link in unique_links:
        url = Url(link)
        if (not url.site_local()):
            ext_links.append(link)
        else:
            linkurl = site_url(link)
            if (linkurl not in page_urls):
                if ((linkurl + "/index.html") not in page_urls):
                    broken_links.append(link)
    if (ext_links):
        section = BuildHtml('''
    <h2>External links</h2>
      <ul>$list</ul>
''')
        li = BuildHtml('<li>$link</li>')
        section.iterate('list', li, 'link', ext_links)
        items.append(section.render())
    if (broken_links):
        section = BuildHtml('''
    <h2>Broken links</h2>
      <ul>$list</ul>
''')
        li = BuildHtml('<li>$link</li>')
        section.iterate('list', li, 'link', broken_links)
        items.append(section.render())
    thehtml = "\n      ".join(items)
    return extras_page(cxt, 'links', "Links", thehtml)


def extras_page(cxt, name, title, contents):
    """Render extras webpage with title and contents; registering it by name.
    For example, "_explore_config" name is "config"; title is "Configuration";
    and contents is the HTML display of the configuration TOML data.
    Returns HTML link to the page that is used to form the extras index page.
    """
    extras_base = "./" + EXTRAS_DIR + "/"
    extras_page = extras_base + name + PAGE_EXTENSION
    webpage = BuildHtml(EXPLORE_HTML)
    webpage.text('title1', title)
    webpage.text('title2', title)
    webpage.insert('contents', contents)
    cxt.extras[extras_page] = webpage.render()
    return htmllink(title, site_url(extras_page))


def line_item(param, value):
    """Returns HTML <li>param: value</li>.
    """
    item = BuildHtml("<li>$param: $value</li>")
    item.text('param', param)
    item.text('value', repr(value))
    return item.render()


EXPLORE_HTML = '''<html>
  <head>
    <title>Explore $title1</title>
    <meta charset="utf8"/>
  </head>
  <body>
    <h1>Explore $title2</h1>
    $contents
    <hr/>
  </body>
</html>
'''
