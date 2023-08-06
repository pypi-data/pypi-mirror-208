"""gdocs: Google Doc integration
There is a test jig for gdoc integration into dirt, for now experimental.
To test _download.toml invocation:
PYTHONPATH='./src' python3 src/dirt/gdocs.py content/
To test download run as a command with a sample document URL argument:
PYTHONPATH='./src' python3 src/dirt/ \
https://docs.google.com/document/d/1y0jCXnwrHw8aI31px7haVPlhgZGuG3HajXYBaYajfgc
NOTE: the document must be publicly shared by link to be accessed
The DOCX file once downloaded is easily converted to markdown with pandoc:
pandoc -f docx -t markdown /tmp/testz.docx >/tmp/markdown.md

Google Doc integration works via a _download.toml file in any content directory
that includes a [gdoc] section with entries per document sourced from the web.
[filename]
    url = "https://docs.google.com/document/d/DOCUMENTID"
    title = "Test document"
This downloads a Google doc from the URL as DOCX and converts it to filename.md
in the current directory using pandoc(1).
List other metadata attributes in alongside 'title' and they will appear
in the attributes at the top of the markdown file.
Attempt to detect unchanged files by hashcode fail; each download is unique.
For now, markdown files must be manually removed when no longer needed.
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2023 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


import hashlib
import os
import re
import requests
import subprocess
import sys
from dirt.config import load_config


DOCX_HASH = "_docx_hash_"


def main(argv=None):
    if (argv[0].startswith("https://docs.google.com/document/")):
        url = argv[0]
        print("Loading %s" % url)
        text = download_doc_text(url)
        print(text)
        print("Downloading DOCX")
        hash = download_doc_file(url, "/tmp/testz.docx")
        print(hash)
    elif (os.path.isdir(argv[0])):
        download_gdocs(argv[0])
    else:
        print("???")


def download_gdocs(dirpath):
    filename = "_download.toml"
    valid_names = r"^[a-zA-Z0-9-_]+$"
    dl = load_config(os.path.join(dirpath, filename))
    if (dl):
        for basename in dl:
            meta_attrs = []
            params = dl[basename]
            for key in params:
                meta_attrs.append("%s: %s" % (key, str(params[key])))
            try:
                if (re.match(valid_names, basename) is None):
                    raise Exception("Invalid name: " + basename)
                url = params.get('url', None)
                if (url):
                    basepath = os.path.join(dirpath, basename)
                    docxpath = basepath + ".docx"
                    docxhash = download_doc_file(url, docxpath)
                    if (docxhash is not None):
                        mdpath = basepath + ".md"
                        pandoc_command = ("pandoc -f docx -t markdown "
                                          + docxpath)
                        process = subprocess.Popen(pandoc_command, shell=True,
                                                   stdout=subprocess.PIPE)
                        markdown = process.communicate()[0].decode("utf-8")
                        with open(mdpath, 'w') as f:
                            f.write('\n'.join(meta_attrs))
                            f.write('\n\n\n')
                            f.write(markdown)
            except Exception as e:
                print("%s: unable to download" % basename)
                print(str(e))


def download_doc_file(doc_url, out_path):
    """Downloads document and writes to a file for conversion.
    Returns SHA-256 hash of the file contents.
    """
    request_url = doc_url + "/export?format=docx"
    doc_bytes = download_doc_data(request_url)
    with open(out_path, 'wb') as f:
        f.write(doc_bytes)
    return hash_bytes(doc_bytes)


def download_doc_text(doc_url):
    """Downloads a Google Doc as plaintext.
    Returns the contents of the Google Doc as plaintext.
    """
    request_url = doc_url + "/export?format=txt"
    doc_bytes = download_doc_data(request_url)
    content = doc_bytes.decode("utf-8")
    return content


def download_doc_data(request_url):
    """Downloads Google Doc data and return the data bytes.
    Raises exception if an error occurs.
    """
    response = requests.get(request_url)
    if response.status_code != 200:
        raise Exception("Error downloading Google Doc: {}".
                        format(response.status_code))
    return response.content


def hash_bytes(byte_array):
    """Compute SHA-256 hash of byte_array and return the hash as hex string.
    """
    hash_value = hashlib.sha256()
    hash_value.update(byte_array)
    return hash_value.hexdigest()


def grab_metadata(filepath):
    """Returns the metadata in the first few lines of markdown file.
    """
    metadata = {}
    with open(filepath, "r") as f:
        for line in f:
            match = re.match(r"^([a-zA-Z_0-9]+): *(.*)$", line)
            if match:
                g = match.groups()
                metadata[g[0]] = g[1]
            else:
                break
    return metadata


if __name__ == '__main__':
    main(sys.argv[1:])


"""
Attempted to optimize by checking hash of DOCX, but every download is unique.
                        if os.path.isfile(mdpath):
                            existing_meta = grab_metadata(mdpath)
                            if existing_meta:
                                existing_hash = existing_meta.get(DOCX_HASH,
                                                                  "").strip()
                                print(existing_hash)
                                print(docxhash)
                                if existing_hash == docxhash:
                                    break
                        meta_attrs.append("%s: %s" % (DOCX_HASH, docxhash))
"""
