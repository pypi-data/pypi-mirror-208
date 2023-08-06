# Copyright 2020 Loren Kohnfelder
# WARNING: This is written for vulnerability research, not production use!
# HTML generation utilities that produce human-readable HTML quickly.
# A bare-bones Web server illustrating common security vulnerabilities.

__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2020 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


import copy
import html
import re
from string import Template
from typing import List
from urllib.parse import quote


INDENTED_REPLACEMENT_REGEX = re.compile(r'^( +)\$([a-z]+)$')


class BuildHtml:
    """HTML content builder for a simple web app.
    For safe results, you must build content correctly by using
    the proper form of template filling method. For example,
    HTML text must be provided to text() method: see below for more.
    When all done, use render() method to construct built string result.
    Indented line substitutions (leading space followed by $KEY only on line)
    cause included content to be indented correspondingly.
    """
    def __init__(self, template, **kwds):
        """Creates new tempalte for HTML string building.
        Additional keyword arguments provide default content values.
        """
        self.template = Template(template)
        self.subs = copy.deepcopy(kwds)
        # Measure indents to apply
        self.indents = dict()
        for line in template.splitlines():
            m = INDENTED_REPLACEMENT_REGEX.match(line)
            if m is not None:
                self.indents[m.group(2)] = m.group(1)

    def _indent(self, key: str, inner: str) -> str:
        if key in self.indents:
            empty = re.compile(r'^ *$')
            prefix = self.indents[key]
            lines: List[str] = []
            for line in inner.split('\n'):
                if not empty.match(line):
                    if len(lines) == 0:
                        # First line is already indented, so don't again.
                        lines.append(line)
                    else:
                        lines.append(prefix + line)
            inner = '\n'.join(lines)
        return inner

    def _quote(self, text):
        """Quote text for the kind of markup being used.
        """
        return html.escape(text, quote=False)

    def insert(self, key: str, content: str):
        """Inserts literal HTML (no escape) that must be safe and syntactic."""
        self.subs[key] = content

    def include(self, key, chunk):
        """Include nested BuildHtml content into a template."""
        inner = chunk.render()
        self.subs[key] = self._indent(key, inner)

    def text(self, key, content):
        """Inserts HTML text (e.g. <p>text here</p>) escaped."""
        self.subs[key] = self._indent(key, self._quote(content))

    def iterate(self, key, chunk, subkey, iterable):
        """Includes zero or more iterations of nested BuildHtml content
        with respective values of the iterable injected with text().
        This is intended for tables or lists that have variable number
        of included sub-elements."""
        result = ''
        for content in iterable:
            chunk.text(subkey, content)
            result = result + self._indent(subkey, chunk.render())
        self.subs[key] = self._indent(key, result)

    def inner(self, key, inner):
        """Converts inner content and inserts (if text) or includes (in HTML)
        it defining the template key. Parameter inner may be BuildHtml
        or text or a list of these.
        """
        if (isinstance(inner, BuildHtml)):
            self.insert(key, inner.render())
        elif (isinstance(inner, str)):
            self.text(key, inner)
        elif (isinstance(inner, list)):
            chunks = list()
            for part in inner:
                if (isinstance(part, BuildHtml)):
                    chunks.append(part.render())
                elif (isinstance(part, str)):
                    chunks.append(self._quote(part))
                else:
                    chunks.append(self._quote(repr(part)))
            self.insert(key, '\n'.join(chunks))
        else:
            self.text('inner', repr(inner))

    def render(self):
        """Renders completed HTML text once all content is provided."""
        return self.template.safe_substitute(self.subs)


class BuildXml(BuildHtml):
    """An XML variant that changes escaping to work properly.
    """
    def _quote(self, text):
        """Quote text for the kind of markup being used.
        """
        return html.escape(text)


def htmltag(tag, inner="", attrs={}):
    """Returns BuildHtml of a tag with attributes wrapping inner content.
    Parameter inner may be text (it's quoted) or BuildHtml (inserted as is);
    any other type is converted to text via repr() and used as text.
    Callers may nest the result in other htmltag calls, or render() into HTML.
    """
    attr_list = list()
    for attr in attrs:
        attr_list.append(' %s="%s"' % (attr, html.escape(attrs[attr])))
    optional_attrs = ''.join(attr_list)
    fragment = BuildHtml('<%s%s>$inner</%s>' % (tag, optional_attrs, tag))
    fragment.inner('inner', inner)
    return fragment


def htmllink(text, url):
    """Returns HTML link text with hyperlink to url.
    """
    return htmltag('a', text, {'href': quote(url)}).render()
