"""Data structure of generated webpage info for the dirt SSG.
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class EntityInfo:
    url: str = ""
    filepath: str = ""


@dataclass
class PageInfo(EntityInfo):
    metadata: Dict[str, str] = field(default_factory=dict)
    mdhtml: str = ""
    links: List[str] = field(default_factory=list)


@dataclass
class DirInfo(EntityInfo):
    parent: str = ""
    pages: List[PageInfo] = field(default_factory=list)
    statics: List[str] = field(default_factory=list)
    collection: Dict[str, str] = field(default_factory=dict)
