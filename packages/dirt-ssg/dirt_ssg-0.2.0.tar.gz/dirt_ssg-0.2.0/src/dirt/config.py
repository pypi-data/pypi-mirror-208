"""config: configuration file processing for dirt SSG
There is a root configuration file (dirt.toml) that provides default
configuration for all dirt websites. This may be overridden at the command
line, but the new config must define all the parameters of dirt.toml.
Generally the configuration of a particular site is handled by _config.toml
in the content/ directory which overrides the backing root (dirt.toml).
When adding a new framework you have to import it here in order to be found.
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


from dirt.common import DirtError, CONFIG_TOML
from dirt.composer import load_framework
from dirt.dirtcontext import DirtContext
from dirt.generate import load_markdown
# Explicitly load subclasses (necessary to reference by name)
import dirt.fx_pico
import dirt.fx_tufte    # noqa: F401

import os
import toml
from typing import List, Optional


def load_config(config_path):
    """Load a config file (toml) and return its defined parameters.
    """
    try:
        with open(config_path, "r") as config_file:
            try:
                config = toml.load(config_file)
            except toml.TomlDecodeError:
                raise DirtError("Bad TOML configuration: %s" % config_path)
    except FileNotFoundError:
        return None
    return config


def site_config(cxt):
    """Process top level site configuration files.
    The site configuration is created in cxt.site.
    At this point we capture the current time as the time of site generation.
    NOTE: for now ignoring metadata on header & footer markdown
    Return a list of filenames processed
    to be skipped walking the source content tree.
    """
    processed = list()
    config = load_config(os.path.join(cxt.content_path, CONFIG_TOML))
    if (config):
        processed.append(CONFIG_TOML)
    else:
        config = dict()
    default_site_config = cxt.defaults['site']
    cxt.site = config_check(config, default_site_config)
    fx = load_framework(cxt, config.get('framework', 'pico'))
    config['framework'] = fx
    config['_header'] = load_markdown_optionally(cxt, processed, "_header.md")
    config['_footer'] = load_markdown_optionally(cxt, processed, "_footer.md")
    fx.setup()
    return processed


def load_markdown_optionally(cxt: DirtContext, processed: List[str],
                             filename: str) -> Optional[str]:
    """Load header or footer markdown for the site iff present.
    If file exists, add to the processed filename list.
    Returns HTML blurb if present or empty string.
    """
    filepath = os.path.join(cxt.content_path, filename)
    if (os.path.isfile(filepath)):
        metadata, mdhtml = load_markdown(filepath)
        processed.append(filename)
        return mdhtml
    return ""


def collection_config(cxt, dirpath):
    """Process collection configuration files if present in each directory.
    Return a 2 element tuple: the collection configuration parameters, a
    list of filenames processed to be skipped walking the source content tree.
    """
    processed = list()
    filename = "_collection.toml"
    config = load_config(os.path.join(dirpath, filename))
    default_config = cxt.defaults['collection']
    if (config):
        processed.append(filename)
        config = config_check(config, default_config)
    else:
        config = default_config
    return config, processed


def config_check(config, defaults):
    """Check that config (dict loaded by toml) is valid and supply defaults.
    The defaults dict contains keys and their default values.
    Valid config values must be the same type as the default value.
    Tables (nested dict) in the config are ignored (they are dynamic).
    Returns config with defaults added, or throws an error if invalid.
    """
    params = list(defaults.keys())
    for key in config:
        value = config[key]
        if (not isinstance(value, dict)):
            if (key in defaults):
                default = defaults[key]
                if (not isinstance(value, type(default))):
                    raise DirtError("Configuration %s is of wrong type: %s"
                                    % (key, repr(value)))
                params.remove(key)
            else:
                raise DirtError("Configuration parameter %s is invalid" % key)
    for key in params:
        config[key] = defaults[key]
    return config
