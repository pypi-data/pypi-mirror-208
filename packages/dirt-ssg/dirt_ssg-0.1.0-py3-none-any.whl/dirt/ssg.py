"""ssg: a dirt simple static site generator library

This is the worker behind the dirt command line that builds the
context and executes the various command line verbs.
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


import dirt.localserver as localserver
from dirt.builder import regenerate
from dirt.checker import link_check
from dirt.common import DirtError, META_DIR, CONFIG_TOML
from dirt.common import dirt_dir
from dirt.config import load_config
from dirt.dirtcontext import DirtContext
from dirt.extras import make_extras

from datetime import datetime, timezone, timedelta
import os
import shutil
from typing import Optional


def cli(args) -> Optional[str]:
    """Invocation via the command line.
    config = path of root (dirt.toml) config file
    input = path of directory containing source content files
    output = path of directory for target generated site files
    localhost = local web server hostname
    port = local web server port number
    verbose = spew verbose standard output
    Returns error message, or None if OK.
    """
    try:
        verb = args.action
        if (verb == "start"):
            result = dirt_start(args)
            if (result):
                return result
            verb = "make"
        cxt = dirt_context(args.config, args.input, args.output)
        if (verb == "make"):
            return regenerate(cxt, verbose=args.verbose)
        elif (verb == "check"):
            error_msg = regenerate(cxt, verbose=args.verbose)
            if (error_msg):
                return error_msg
            return link_check(cxt, verbose=args.verbose)
        elif (verb != "server"):
            return "Invalid action: %s" % args.action
        error_msg = regenerate(cxt, verbose=args.verbose)
        if (error_msg):
            return error_msg
        make_extras(cxt)
        localserver.serve_forever(cxt, args.localhost, args.port,
                                  not args.noautoupdate, args.verbose)
        return None
    except DirtError as e:
        return e.message


def dirt_context(config_path: str, input_path: str, output_path: str
                 ) -> DirtContext:
    """Create dirt context from command line args.
    Load dirt.toml root configuration (at config_path);
    input_path is content source, output_path is target directory.
    _site.toml site configuration in the source content directory (if present),
    build and return context.
    """
    if (not os.path.isdir(input_path)):
        raise DirtError("Expected content directory: %s" % input_path)
    if (os.path.realpath(input_path) == os.path.realpath(output_path)):
        output_path = os.path.join(output_path, "_site")
    if (not os.path.isdir(output_path)):
        if (os.path.exists(output_path)):
            raise DirtError("Target site is not a directory: %s" % output_path)
        else:
            os.makedirs(output_path)
    dirt_config = load_config(config_path)
    if (dirt_config is None):
        raise DirtError("Missing dirt configuration file: %s" % config_path)
    cxt = DirtContext()
    cxt.build_time = datetime.now(timezone(timedelta(), "GMT"))
    cxt.config = dirt_config
    cxt.content_path = input_path
    cxt.public_path = output_path
    cxt.defaults = dirt_config['defaults']
    filetypes = dirt_config['filetypes']
    cxt.static_types = filetypes['static_types']
    cxt.page_types = filetypes['page_types']
    return cxt


def dirt_start(args):
    """The dirt start command supports getting started using dirt.
    Usually invoked in an empty directory, this creates a minimal
    dirt website as a starting template:
    content/index.md
    content/_config.toml file.
    """
    cont_path = args.input
    if (os.path.isfile(cont_path)):
        return ("Cannot create files into an existing file. [%s]"
                % cont_path)
    if (os.path.isdir(cont_path)):
        entries = os.scandir(cont_path)
        count = 0
        for entry in entries:
            count += 1
        if (count):
            return ("Cannot create files into an existing directory. [%s]"
                    % cont_path)
    else:
        os.makedirs(cont_path)
    print("Welcome to the dirt SSG!")
    print("Create your website by editing these simple starting files.")
    created_path = create_content_file(cont_path, 'index.md')
    print("  Edit the homepage markdown prototype: %s" % created_path)
    created_path = create_content_file(cont_path, CONFIG_TOML)
    print("  Customize the configuration file: %s" % created_path)
    return None


def create_content_file(basepath, filename):
    """Create a content file as part of dirt start command.
    Returns the path of the newly created file.
    """
    sourcepath = os.path.join(dirt_dir(META_DIR), filename)
    destinationpath = os.path.join(basepath, filename)
    shutil.copyfile(sourcepath, destinationpath)
    return destinationpath
