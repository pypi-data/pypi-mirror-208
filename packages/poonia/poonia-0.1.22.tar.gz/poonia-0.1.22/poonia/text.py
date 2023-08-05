from html.parser import HTMLParser
import re

_BOLD_TAGS = {'b', 'strong'}
_ITALIC_TAGS = {'i', 'em'}
_IGNORE_TAGS = {'script', 'style'}


class _HTMLTextParser(HTMLParser):
    def __init__(self):
        super(_HTMLTextParser, self).__init__(convert_charrefs=True)
        self.bold = []
        self.italic = []
        self.tag_bold = 0
        self.tag_italic = 0
        self.tag_ignore = 0
        self.parsed_text = []

    def handle_starttag(self, tag, attr_list):
        if tag in _BOLD_TAGS:
            self.tag_bold += 1
        elif tag in _ITALIC_TAGS:
            self.tag_italic += 1
        elif tag in _IGNORE_TAGS:
            self.tag_ignore += 1
        elif tag == 'br':
            self.handle_data('\n', replace_whitespace=False)

    def handle_endtag(self, tag):
        if tag in _BOLD_TAGS:
            self.tag_bold -= 1
        elif tag in _ITALIC_TAGS:
            self.tag_italic -= 1
        elif tag in _IGNORE_TAGS:
            self.tag_ignore -= 1

    def handle_data(self, data, replace_whitespace=True):
        if self.tag_ignore > 0:
            return
        if replace_whitespace:
            data = re.sub(r'\s+', ' ', data)
        self.bold += [self.tag_bold > 0]*len(data)
        self.italic += [self.tag_italic > 0]*len(data)
        self.parsed_text.append(data)


class RichText(str):
    def __new__(cls, html):
        parser = _HTMLTextParser()
        parser.feed(html)
        s = super().__new__(cls, ''.join(parser.parsed_text))
        s.bold = parser.bold
        s.italic = parser.italic
        return s
