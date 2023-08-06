"""checker: automated website checking for dirt SSG
Link validity checking is the first feature: internal links and external links.
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


from dirt.common import site_url
from dirt.urls import Url

import time
import urllib.request
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse


USER_AGENT = "Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36 (KHTML,\
 like Gecko) Raspbian Chromium/78.0.3904.108 Chrome/78.0.3904.108\
 Safari/537.36"
CONNECTION_ERROR = -99999


def link_check(cxt, verbose=False):
    """Checks links in the website and reports error message, or None if OK.
    """
    page_links = list()
    page_urls = list()
    for dirname in cxt.dirs:
        dirinfo = cxt.dirs[dirname]
        pages = dirinfo.pages
        if (pages):
            for page in pages:
                page_urls.append(page.url)
                for link in page.links:
                    linkurl = Url(link)
                    page_links.append(linkurl.effective(page.url))
    unique_links = set(page_links)
    if (verbose):
        numbers = (len(page_links), len(unique_links), len(page_urls))
        print("Total links: %d (%d unique); website pages: %d" % numbers)
    ext_links = list()
    broken_links = list()
    for link in unique_links:
        url = Url(link)
        if (not url.site_local()):
            ext_links.append(link)
        else:
            parsed = urlparse(link)  # get only the path, without fragment
            linkurl = site_url(parsed.path)
            print(linkurl)
            if (linkurl not in page_urls):
                if ((linkurl + "/index.html") not in page_urls):
                    broken_links.append(link)
    failed_ext = web_check(ext_links, verbose)
    if (broken_links or failed_ext):
        detail = list()
        for failed in failed_ext:
            detail.append("%15s: %s" % failed)
        for broken in broken_links:
            detail.append("%15s: %s" % ("No such page", broken))
        return '\n'.join(detail)
    return None


def web_check(ext_links, verbose=False):
    """Check for links on the web and return pairs for any failures.
    Returns a list of (short_diagnostic_text, URL_string) detailing failures.
    """
    failed_ext = list()
    for link in ext_links:
        error = web_check_url(link)
        if (error):
            failed_ext.append((error, link))
    return failed_ext


def web_check_url(url, verbose=False):
    """Check an url for viability. Returns short error message or None is OK.
    """
    if not vet_url(url):
        return "Invalid URL"
    time_started = time.time()
    (content, response) = fetch_url(url)
    time_loaded = time.time()
    time_elapsed = round(time_loaded - time_started, 1)
    if (verbose):
        print("%40s ==> %4.2fs %s" % (url, time_elapsed, repr(response)))
    if (response.get('redirects', [])):
        return "Redirect"
    code = response['code']
    if code == 200:
        if (len(content) == 0):
            return "Zero length"
    else:
        if code == CONNECTION_ERROR:
            return "Connection error"
        if code in [401, 402, 403, 410]:
            return "Blocked(%d)" % code
        elif code in [400, 404, 406]:
            return "Refused(%d)" % code
    return None


def vet_url(url):
    """Parse and vet an URL if dokumi will work with it or not.
    """
    try:
        parts = urlparse(url)
        if parts.scheme in ['http', 'https']:
            return True
    except ValueError:
        pass
    return False


hook_redirect = []


class HookHTTPRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Hook the redirect handler to get the full chain of requests."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        global hook_redirect
        hook_redirect.append((code, newurl))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_url(url):
    """Fetch the given url synchronously are return details of what happened.
    Returns (content, response): the first is the content at the URL;
    the second has various parameters characterizing aspects of the results.
    'actual_url': the actual URL after redirects
    'code': HTTP response code
    'content_type': HTTP content type, e.g. 'text/html; charset=utf-8',
    'info': headers and other info
    'redirects': a list of details from any redirects incurred
    """
    results = {'actual_url': None, 'code': None, 'info': None, 'redirects': []}
    content = None
    try:
        # Hook HTTP redirects
        global hook_redirect
        hook_redirect = []
        opener = urllib.request.build_opener(HookHTTPRedirectHandler)
        urllib.request.install_opener(opener)

        request = urllib.request.Request(url, data=None,
                                         headers={'User-Agent': USER_AGENT})
        response = urllib.request.urlopen(request)
        content = response.read()
        results['actual_url'] = response.geturl()
        results['code'] = response.getcode()
        results['redirects'] = hook_redirect
        headers = response.info().items()
        results['info'] = headers
        for header in headers:
            header_name = header[0].casefold()
            header_value = header[1].casefold()
            if header_name == 'content-type':
                results['content_type'] = header_value

    except HTTPError as fail:
        results['code'] = fail.code
        results['info'] = fail.reason if hasattr(
            fail, 'reason') else repr(fail)
    except URLError as fail:
        results['code'] = CONNECTION_ERROR if (
            fail.errno is None) else fail.errno
        results['info'] = fail.reason if hasattr(
            fail, 'reason') else repr(fail)
    except ConnectionResetError as fail:
        results['code'] = CONNECTION_ERROR
        results['info'] = fail.reason if hasattr(
            fail, 'reason') else repr(fail)

    return (content, results)
