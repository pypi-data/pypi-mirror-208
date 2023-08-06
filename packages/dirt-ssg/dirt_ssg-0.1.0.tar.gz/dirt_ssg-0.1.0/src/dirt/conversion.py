"""conversion: conversion from markdown text to HTML for dirt SSG
Encapsulate markdown conversion with dirt-specific extensions.
This module can be invoked from the command line to convert stdin to stdout.
For testing, most dirt markdown is in content/ and doc/ directories.
Reference: https://python-markdown.github.io/extensions/api/
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2023 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


import markdown
import re
import sys

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.treeprocessors import Treeprocessor
from dirt.words import unique_anchor
import xml.etree.ElementTree as etree


class DashInlineProcessor(InlineProcessor):
    """Dash processor for dirt markdown.
    Convert "---" to em-dash "—".
    Emitting <span> tag because I don't know how to just emit a character.
    """
    def handleMatch(self, m, data):
        el = etree.Element('span')
        el.text = "\u2014"
        return el, m.start(1), m.end(1)


class DashExtension(Extension):
    """Dash extension for markdown conversion.
    Example use: exactly three consecutive hyphens --- in text.
    """
    def extendMarkdown(self, md):
        DASH_PATTERN = r'[^-]??(---)[^-]??'
        md.inlinePatterns.register(DashInlineProcessor(DASH_PATTERN, md),
                                   'dash', 175)


class DelInlineProcessor(InlineProcessor):
    """Strikeout inline processor for markdown conversion.
    Courtesy: https://python-markdown.github.io/extensions/api/
    """
    def handleMatch(self, m, data):
        el = etree.Element('del')
        el.text = m.group(1)
        return el, m.start(0), m.end(0)


class DelExtension(Extension):
    """Strikeout extension for markdown conversion.
    Example use: --this is strike out-- text.
    """
    def extendMarkdown(self, md):
        DEL_PATTERN = r'--([^-]*?)--'
        md.inlinePatterns.register(DelInlineProcessor(DEL_PATTERN, md),
                                   'del', 175)


class BoxBlockProcessor(BlockProcessor):
    """Extension to python markdown to enclose content in a box frame.
    Courtesy: https://python-markdown.github.io/extensions/api/
    """
    RE_FENCE_START = r'^ *!{3,} *\n'
    RE_FENCE_END = r'\n *!{3,}\s*$'

    def test(self, parent, block):
        return re.match(self.RE_FENCE_START, block)

    def run(self, parent, blocks):
        original_block = blocks[0]
        blocks[0] = re.sub(self.RE_FENCE_START, '', blocks[0])
        # Find block with ending fence
        for block_num, block in enumerate(blocks):
            if re.search(self.RE_FENCE_END, block):
                # remove fence
                blocks[block_num] = re.sub(self.RE_FENCE_END, '', block)
                # render fenced area inside a new div
                e = etree.SubElement(parent, 'div')
                e.set('style',
                      'display: inline-block; border: 1px solid red;')
                self.parser.parseBlocks(e, blocks[0:block_num + 1])
                # remove used blocks
                for i in range(0, block_num + 1):
                    blocks.pop(0)
                return True  # or could have had no return statement
        # No closing marker!  Restore and do nothing
        blocks[0] = original_block
        return False  # equivalent to our test() routine returning False


class BoxExtension(Extension):
    """Text box extension for markdown conversion.
    """
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(BoxBlockProcessor(md.parser),
                                           'box', 176)


class DirtInlineProcessor(InlineProcessor):
    """Dirt inline processor for dirt markdown.
    Apply an HTML tag such as <sup> or <sub> by enclosing it in curlies ({})
    before the markdown text it applies to, terminated by empty curlies ({}).
    {tag}markdown contents here{}
    Alternatively, write a styling expression enclosed by double quotes. Ex:
    {"styling-expression..."}markdown contents here{}
    The above will be rendered as <span style="styling-expression..."> ...
    """
    def handleMatch(self, m, data):
        styling = re.match(r'^"(.+)"$', m.group(1))
        if styling:
            el = etree.Element('span')
            el.set('style', styling.group(1))
        else:
            el = etree.Element(m.group(1))
        el.text = m.group(2)
        return el, m.start(0), m.end(0)


class DirtInlineExtension(Extension):
    """Dirt extension for markdown conversion. See processor comments for more.
    {tag}markdown contents here{}
    {"styling-expression..."}markdown contents here{}
    """
    def extendMarkdown(self, md):
        STYLE_PATTERN = r'[{](.+?)[}](.+?)[{][}]'
        md.inlinePatterns.register(DirtInlineProcessor(STYLE_PATTERN, md),
                                   'style', 175)


class DirtTreeProcessor(Treeprocessor):
    """Tree processor for dirt SSG features: make anchors for section headings.
    This gets called once with the HTML element tree of the converted markdown.
    This root has an outer <div><blockquote>...</div> wrapper that's ignored.
    """
    def __init__(self, md, headings):
        super(DirtTreeProcessor, self).__init__(md)
        self.headings = headings

    def run(self, root):
        for level in range(1, 10):
            for heading in root.findall("h%d" % level):
                hid = unique_anchor(self.headings, heading.text)
                heading.set("id", hid)
                heading.set("title", "#" + hid)
                self.headings.append(hid)


class DirtTreeExtension(Extension):
    """An extension for dirt markdown conversion.
    """
    def __init__(self, headings):
        self.headings = headings

    def extendMarkdown(self, md):
        md.treeprocessors.register(DirtTreeProcessor(md.parser, self.headings),
                                   'dirt', 25)


class Markdown2Html:
    """HTML conversion from markdown text for dirt SSG.
    Create an instance where markdown engine is initialized,
    then repeatedly call the convert method on each chunk of markdown.
    """
    def __init__(self, extensions=None):
        """Creates new markdown engine instance with specified extensions,
        or dirt's default extensions if unspecified.
        """
        self.headings = []
        if extensions is None:
            extensions = ['footnotes', 'meta', 'tables', DirtInlineExtension(),
                          DirtTreeExtension(self.headings),
                          BoxExtension(), DashExtension(), DelExtension()]
        self._markdown_engine = markdown.Markdown(extensions=extensions)

    def convert(self, markdown_text):
        """Returns markdown_text string converted to an HTML text string.
        """
        self.headings.clear()
        self._markdown_engine.reset()
        html_text = self._markdown_engine.convert(markdown_text)
        return html_text

    def metadata(self):
        return self._markdown_engine.Meta


def main(args):
    """Command line for testing to convert stdin markdown to HTML as stdout.
    (Command line arguments are ignored for now.)
    """
    converter = Markdown2Html()
    markdown_text = sys.stdin.read()
    html_text = converter.convert(markdown_text)
    sys.stdout.write(html_text + "\n")


if __name__ == '__main__':
    main(sys.argv[1:])
