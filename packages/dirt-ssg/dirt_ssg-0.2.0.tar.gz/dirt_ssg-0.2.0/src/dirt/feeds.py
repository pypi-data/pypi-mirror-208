"""feeds: static site generator feed generation for dirt SSG
Site configuration [feed] table defines RSS feeds generated from page info
collections in site directories, using the same ordering.
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


from dirt.common import canonical_rel
from dirt.htmlify import BuildXml
from dirt.words import excerpt

import os
from urllib.parse import urljoin, quote


def make_feeds(cxt):
    """Generate RSS feed files as specified in site configuration [feed] table.
    Returns list of files generated.
    Example:
    [feed.sub]
        channel = "sub"
        title = "Subsidiary sample files"
        description = "Describe the RSS channel"
        url = "sub.xml"
    excerpt = 3
    count = 12
    LastBuildDate is RFC822, e.g. "Sat, 16 Jul 2022 08:31:40 GMT" (not "UTC")
    Validate at https://validator.w3.org/feed/check.cgi
    """
    host_url = cxt.config.get('host_url', 'http://localhost')
    now = cxt.build_time
    build_date = now.strftime('%a, %d %b %Y %H:%M:%S %Z')
    feed_template = cxt.snippets['rss_feed']
    item_template = cxt.snippets['rss_item']
    feeds = cxt.site.get('feed', [])
    target_path = cxt.public_path
    files_generated = list()
    for feedname in feeds:
        feed = feeds[feedname]
        dirname = canonical_rel(feed.get('channel', ""))
        title = feed.get('title', "(untitled)")
        desc = feed.get('description', "(none)")
        url = feed.get('url', "%s.rss" % feedname)
        full_path = urljoin(host_url, quote(url))
        excerpt_paras = feed.get('excerpt', 0)
        maxcount = feed.get('count', 9999999999)
        feed_xml = BuildXml(feed_template)
        feed_xml.text('title', title)
        feed_xml.text('description', desc)
        feed_xml.text('link', host_url)
        feed_xml.text('feedurl', full_path)
        feed_xml.text('LBD', build_date)
        dirinfo = cxt.dirs.get(dirname, None)
        pages = dirinfo.pages if (dirinfo) else []
        items = list()
        for page in pages:
            if (page.metadata.get('_index', False)):
                continue
            item = BuildXml(item_template)
            title = page.metadata.get('title', '(untitled)')
            html_desc = page.mdhtml
            if (excerpt_paras):
                html_desc = excerpt(html_desc, maxparas=excerpt_paras)
            description = wrap_html(html_desc)
            page_url = urljoin(host_url, quote(page.url))
            item.text('title', title)
            item.insert('description', description)
            item.text('link', page_url)
            item.text('guid', page_url)
            items.append(item.render())
            if (len(items) >= maxcount):
                break
        feed_xml.insert('items', "".join(items))
        feed_content = feed_xml.render()
        feed_path = os.path.join(target_path, url)
        with open(feed_path, 'w') as f:
            f.write(feed_content)
        feed['_url'] = canonical_rel(url)
        files_generated.append(url)
    return files_generated


def wrap_html(html):
    """Wrap page HTML within XML CDATA for RSS feed.
    TODO: BUG If the html happens to contain the 3 chars ]]> it closes CDATA.
    """
    return "".join(['<![CDATA[', html, ']]>'])
