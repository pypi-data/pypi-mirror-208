"""fx_pico: the pico CSS framekwork composer for dirt SSG
Documentation: https://picocss.com/docs/
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


from dirt.composer import DirtFramework
from dirt.htmlify import BuildHtml, htmllink, htmltag
from dirt.words import sections_of_html


class PicoFramework(DirtFramework):
    """Pico framework rendering HTML for dirt.
    """
    def setup(self):
        """Setup framework ahead of composing pages."""
        super(PicoFramework, self).setup()
        self.make_snippet('_pico_html', ["pico_template.html"])

    def compose(self, mdhtml: str, meta: dict) -> str:
        """Compose a pico HTML page from converted markdown HTML & metadata.
        Parts of the page to compose:
        header, body, previews, footer
        """
        sections = sections_of_html(mdhtml)
        chunks = list()
        for section in sections:
            chunks.append("<section>\n%s</section>" % section)
        html = '\n'.join(chunks)
        injecthtml = self.expand(meta, html)
        navtop, navbottom = self.navigation(meta)
        page = BuildHtml(self.cxt.snippets['_pico_html'])
        page.text('title', self.page_title(meta))
        header_html = self.expand(meta, self.page_param({}, '_header', ''))
        page.insert('header', header_html + navtop)
        page.insert('body', injecthtml + self.inject_previews(meta, 'h2'))
        footer_html = self.expand(meta, self.page_param({}, '_footer', ''))
        page.insert('footer', navbottom + footer_html)
        return page.render()

    def expansion(self, keyword):
        """Provide HTML expansion of keywords for the pico framework.
        <details role="list">
        <summary aria-haspopup="listbox">Dropdown</summary>
        <ul role="listbox">
        <li><a>Action</a></li><li><a>Something</a></li>
        </ul></details>
        """
        if (keyword == "menu"):
            menu_table = self.cxt.site[keyword]
            items = list()
            for key in menu_table:
                url = menu_table[key]
                items.append("    <li>" + htmllink(key, url) + "</li>\n")
            summary_html = htmltag('summary', "Menu",
                                   {'aria-haspopup': "listbox"})
            ul_html = htmltag('ul', BuildHtml("".join(items)),
                              {'role': "listbox"})
            menu_html = htmltag('details', [summary_html, ul_html],
                                {'role': "list"})
            return menu_html.render()
        return None

    def page_link(self, page, untitled):
        """Returns HTML link to a page for composing navigation controls.
        If the page has no title, use untitled string instead.
        This override makes button links.
        """
        title = self.page_param(page.metadata, 'title', untitled)
        return htmltag('a', title, {'href': page.url, 'role': 'button'}
                       ).render()
