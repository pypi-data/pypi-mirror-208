"""fx_tufte: Tufte framework page composer for a dirt SSG
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


from dirt.htmlify import BuildHtml
from dirt.composer import DirtFramework
from dirt.words import sections_of_html


class TufteFramework(DirtFramework):
    def setup(self):
        """Framework setup for tufte before SSG generates pages.
        """
        super(TufteFramework, self).setup()
        self.make_snippet('_tufte_html', ["tufte_template.html"])

    def compose(self, mdhtml: str, meta: dict) -> str:
        """Compose a tufte HTML page from converted markdown HTML & metadata.
        """
        sections = sections_of_html(mdhtml)
        chunks = list()
        for section in sections:
            chunks.append("<section>\n%s</section>" % section)
        html = '\n'.join(chunks)
        injecthtml = self.expand(meta, html)
        page = BuildHtml(self.cxt.snippets['_tufte_html'])
        page.text('title', self.page_title(meta))
        header_html = self.expand(meta, self.page_param({}, '_header', ''))
        page.insert('header', header_html)
        previews = self.inject_previews(meta, 'h1')
        if (previews):
            previews = "<section>\n%s</section>\n" % previews
        page.insert('body', injecthtml + previews)
        footer_html = self.expand(meta, self.page_param({}, '_footer', ''))
        page.insert('footer', footer_html)
        return page.render()
