"""Dirt context object carries configuration and site data for the SSG.
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


from dirt.pageinfo import PageInfo

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class DirtContext:
    content_path: str = None
    public_path: str = None
    dirs: Dict[str, PageInfo] = field(default_factory=dict)
    defaults: Dict[str, str] = None
    static_types: List[str] = None
    page_types: List[str] = None
    framework = None
    config: Dict[str, str] = None
    site: Dict[str, str] = field(default_factory=dict)
    timestamp: str = ''
    snippets: Dict[str, str] = field(default_factory=dict)
    build_time: datetime = None
    extras: Dict[str, str] = field(default_factory=dict)
