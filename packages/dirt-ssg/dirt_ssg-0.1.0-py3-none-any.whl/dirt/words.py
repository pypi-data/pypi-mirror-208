"""words: HTML and text handling for a dirt simple static site generator
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


from dirt.common import DirtError
from dirt.htmlify import htmllink
from dirt.pageinfo import PageInfo

import random
import re
from typing import List


REGEX_NONALPHA = re.compile(r'[^ \w\d]')


def curly_expander(htmltext, resolver):
    """Expand {expressions} within HTML content pages, replacing with HTML.
    Uses resolver(keyword) to fetch replacement HTML.
    Changed the syntax to {$identifier} to avoid most conflicts or accidents.
    TODO: Bug if this picks up {something} that is in the content text.
    Returns HTML with {expressions} expanded
    """
    lines = htmltext.split('\n')
    for seq in range(len(lines)):
        line = lines[seq]
        m = re.search(r'[{][$]([_a-zA-Z]+)[}]', line)
        if (m):
            keyword = m.group(1)
            replacement = resolver(keyword)
            line = line[0:m.start()] + as_html(replacement) + line[m.end():]
        lines[seq] = line
    return '\n'.join(lines)


def as_html(obj):
    """Returns HTML insertion for obj: int, str, or PageInfo.
    """
    if (obj is None):
        return ''
    typ = type(obj)
    if (typ == int):
        return str(obj)
    if (typ == str):
        return obj
    if (typ == PageInfo):
        meta = obj.metadata
        titletext = meta['title']
        return htmllink(titletext, obj.url)
    raise DirtError("Invalid {expression}: %s" % str(typ))


def excerpt(htmltext, maxchar=8000, maxlines=50, maxparas=10):
    """Returns shortened excerpt of leading part of HTML text.
    Excerpts are no longer than (maxchar) characters, (maxparas) paragraphs,
    or (maxlines) lines, whichever is shorter.
    TODO Buggy when HTML tags are truncated unclosed
    """
    lines = htmltext.split('\n')
    paras = 0
    chars = 0
    result = list()
    for seq in range(len(lines)):
        line = lines[seq]
        chars = chars + len(line)
        if (re.match('^<P>', line, re.IGNORECASE)):
            paras = paras + 1
        result.append(line)
        if (chars > maxchar or seq >= maxlines or paras >= maxparas):
            break
    return '\n'.join(result)


def sections_of_html(mdhtml: str) -> List[str]:
    """Returns a list of sections of markdown-produced HTML for the framework.
    Input {html} text is lines of HTML out of the markdown converter.
    Sections are runs of lines with heading(s) at top, up to the next heading.
    TODO: Move this to the markdown tree processor.
    TODO: Don't be fooled by embedded HTML.
    """
    lines: List[str] = mdhtml.split('\n')
    sections: List[str] = list()
    section: List[str] = list()
    nonheader_lines = 0
    for line in lines:
        if (re.match(r'^<h[1-9][ >]', line)):
            if (nonheader_lines):
                html = '\n'.join(section)
                sections.append(html)
                section = list()
                nonheader_lines = 0
        else:
            nonheader_lines += 1
        section.append(line)
    if (section):
        html = '\n'.join(section)
        sections.append(html)
    return sections


def unique_anchor(ids, text):
    """Derive a unique anchor from full text suitable for an HTML id attribute.
    For example, shorten heading "Chapter One" to "chap-one".
    Most importantly, the result may not be identical to any already in ids.
    For several cases some candidates are made, the first unique one is used,
    or at the end a random variant is the final alternative.
    """
    shortn = 5   # Preferred short length of words
    idsafe = REGEX_NONALPHA.sub('', text.lower())
    words = idsafe.split(' ')
    if len(words) < 1 or len(words[0]) == 0:
        cand = ["id-%d" % (1 + len(ids))]
    elif len(words) == 1:
        if len(words[0]) < 12:  # Prefer whole word unless very long
            cand = [words[0], words[0][:shortn]]
        else:
            cand = [words[0][:shortn], words[0]]
    elif len(words) >= 2:
        cand = [words[0][:shortn] + '-' + words[1][:shortn]]
        cand.append(words[0] + '-' + words[1])
        for i in range(2, len(words)):
            cand.append(words[0][:shortn] + '-' + words[i][:shortn])
            cand.append(words[0] + '-' + words[i])
    # Find first candidate that's unique
    for item in cand:
        if item not in ids:
            return item
    for suffix in range(1, 8):
        for item in cand:
            itemx = "%s%d" % (item, suffix)
            if itemx not in ids:
                return itemx
    # Last ditch is randomness (this has to work eventually)
    for length in range(4, 30):
        suffix = ("%x" % random.randint(0, 999999999999))[:length]
        for item in cand:
            itemx = "%s-%s" % (item, suffix)
            if itemx not in ids:
                return itemx
    # Give up (should never happen)
