"""Implements a barebones static file Web server to make dirt SSG use a breeze.
All custom code specific to dirt is here; server.py is a generic base class.
"""

__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


from dirt.builder import regenerate
import dirt.common as common
from dirt.common import ignore_file
from dirt.generate import addon_script
from http.server import HTTPServer
import mimetypes
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from http import server


def mime_guesser(path: str) -> str:
    guess = mimetypes.guess_type(path)
    if guess[0] is None:
        return 'application/octet-stream'
    else:
        return guess[0]


class DirtStaticStorage:
    def __init__(self, public_path, extras={}):
        """Static storage wrapper to read files at the given path for serving.
        """
        self.static_dir = public_path
        self.root_filename = common.INDEX_FILE + common.PAGE_EXTENSION
        self.extras = extras

    def get_file(self, pathname):
        """Maps request pathnames to static files for serving.
        Returns inferred mime type and file content for response.
        """
        assert pathname[0] == '/'
        pathname = "." + pathname
        if (pathname in self.extras):
            mimetype = mime_guesser(pathname)
            return mimetype, self.extras[pathname].encode()
        else:
            filepath = os.path.join(self.static_dir, pathname)
            if (os.path.isdir(filepath)):
                filepath = os.path.join(filepath, self.root_filename)
            mimetype = mime_guesser(filepath)
            with open(filepath, mode='rb') as file:
                return mimetype, file.read()


class DirtHandler(server.BaseHTTPRequestHandler):
    """A custom Web request handler for the dirt SSG.
    This overrides the base request handler providing URL parsing
    and dispatch to serve the respective pages of the website.
    """
    def __init__(self, cxt, storage, verbose=False):
        self.cxt = cxt
        self.storage = storage
        self.verbose = verbose

    def __call__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def static(self, pathname, content_type=''):
        """Request for static file content.
        Assume paths always begin with / and are relative to site root.
        """
        try:
            mimetype, data = self.storage.get_file(pathname)
            if content_type == '':
                content_type = mimetype
            if (content_type == "text/html"):
                dirt_config = self.cxt.config
                interval = dirt_config.get('refresh_interval', 1)
                addon = addon_script(self.cxt, interval=interval)
                data += str.encode(addon)

            self.send_response(200)
            self.send_header('Cache-Control', 'public, max-age=1')
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            return self.nosuch()

    def nosuch(self, message=''):
        """Fail unknown URL paths."""
        self.send_response(404)
        self.end_headers()
        if message == '':
            msg = 'Invalid request URL [%s].' % self.path
        else:
            msg = 'Error: %s [%s]' % (message, self.path)
        self.wfile.write(msg.encode('utf-8'))

    def do_GET(self):
        """Web application handler dispatch for HTTP GET requests.
        Overrides the default 'under construction' method.
        """
        return self.static(self.path)

    def do_POST(self):
        """Web application handler dispatch for HTTP POST requests.
        Overrides the default 'under construction' method.
        """
        self.send_response(405)
        self.end_headers()

    def log_request(self, code='-', size='-'):
        """Log HTTP request from http.server.BaseHTTPRequestHandler.
        Override to filter out 200.
        """
        if (self.verbose):
            return super(DirtHandler, self).log_request(code, size)


def serve_forever(cxt, hostname='localhost', port=1313,
                  auto_update=False, verbose=False):
    """Service loop for localhost HTTP requests.
    """
    class UpdateHandler(FileSystemEventHandler):
        """File update handler for monitoring changes
        in the source content directory.
        """
        def on_closed(self, event):
            if (not event.is_directory):
                return self.delta(event.src_path)

        def on_deleted(self, event):
            if (not event.is_directory):
                return self.delta(event.src_path)

        def on_moved(self, event):
            if (not event.is_directory):
                return self.delta(event.dest_path)

        def update(self, event):
            if (not event.is_directory):
                return self.delta(event.src_path)

        def delta(self, path):
            if (ignore_file(os.path.basename(path))):
                return
            if (path.endswith(".dirt")):
                return
            # TODO wipe should be an option
            error = regenerate(cxt, verbose=False)
            if (verbose):
                if (error):
                    print("autoupdate error: " + error)
                else:
                    print("autoupdate success: " + cxt.timestamp)
            return

    content_path = cxt.content_path
    public_path = cxt.public_path
    if (auto_update):
        observer = Observer()
        observer.schedule(UpdateHandler(), content_path, recursive=True)
        observer.start()
    server_address = (hostname, port)
    print('Serving http://%s:%d ...' % server_address)
    storage = DirtStaticStorage(public_path, cxt.extras)
    handler = DirtHandler(cxt, storage, verbose)
    httpd = HTTPServer(server_address, handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(' ... Bye.')
    finally:
        if (auto_update):
            observer.stop()
            observer.join()
