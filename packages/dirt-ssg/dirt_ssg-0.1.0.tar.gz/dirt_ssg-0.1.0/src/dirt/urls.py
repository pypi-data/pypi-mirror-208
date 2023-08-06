"""urls: URL handling for the dirt SSG
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


from urllib.parse import urlparse, urljoin


class Url:
    def __init__(self, link):
        """Interpretation for a link as an URL on a webpage.
        """
        self.link = link
        self.parsed = urlparse(link)

    def site_local(self):
        """Returns whether the URL link is local to the site or has hostname.
        """
        return not self.parsed.hostname

    def effective(self, baseurl: str):
        """Returns a site-local URL as an absolute site-local URL.
        Example: on the page dir/sub/page link ../example will be /dir/example.
        """
        if (not self.site_local()):
            return self.link
        result = urljoin(baseurl, self.link)
        if (result[0] != '/'):
            return '/' + result
        return result
