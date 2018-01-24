#!/usr/bin/env python
# coding: utf-8
"""html2text: Turn HTML into equivalent Markdown-structured text."""
from __future__ import division
from __future__ import unicode_literals
import re
import sys


from html2text.compat import urlparse, HTMLParser
from html2text import config

from html2text.utils import (
    name2cp,
    element_style,
    hn,
    list_numbering_start,
    dumb_css_parser,
    convert_superscript,
    pad_tables_in_text
)

try:
    chr = unichr
    nochr = unicode('')
except NameError:
    # python3 uses chr
    nochr = str('')

__version__ = (2017, 10, 4)


class HTML2Text(HTMLParser.HTMLParser):
    def __init__(self, out=None, baseurl=''):
        """
        Input parameters:
            out: possible custom replacement for self.outtextf (which
                 appends lines of text).
            baseurl: base URL of the document we process
        """
        kwargs = {}
        if sys.version_info >= (3, 4):
            kwargs['convert_charrefs'] = False
        HTMLParser.HTMLParser.__init__(self, **kwargs)

        # Config options
        self.split_next_td = False
        self.td_count = 0
        self.table_start = False
        self.links_each_paragraph = config.LINKS_EACH_PARAGRAPH
        self.skip_internal_links = config.SKIP_INTERNAL_LINKS  # covered in cli
        self.inline_links = config.INLINE_LINKS  # covered in cli
        self.images_to_alt = config.IMAGES_TO_ALT  # covered in cli
        self.bypass_tables = config.BYPASS_TABLES  # covered in cli
        self.ignore_tables = config.IGNORE_TABLES  # covered in cli
        self.ul_item_mark = '*'  # covered in cli
        self.emphasis_mark = '_'  # covered in cli
#        self.emphasis_mark_start = config.bcolors.YELLOW
#        self.emphasis_mark_end = config.bcolors.ENDC
#        self.strong_mark_start = config.bcolors.BOLD
#        self.strong_mark_end = config.bcolors.ENDC
        self.emphasis_mark_start = '\N{INVISIBLE SEPARATOR}' #\u2063
        self.emphasis_mark_end = '\N{INVISIBLE SEPARATOR}'*2 #\u2063
        self.strong_mark_start = '\N{INVISIBLE SEPARATOR}' #\u2063
        self.strong_mark_end = '\N{INVISIBLE SEPARATOR}'*3 #\u2063
        self.underline_mark_start = config.bcolors.UNDERLINE
        self.underline_mark_end = config.bcolors.ENDC
        self.strong_mark = '**'
        #self.link_begin_mark = config.bcolors.OKBLUE
        self.link_begin_mark = '\N{INVISIBLE SEPARATOR}' #\u2063
        #self.link_end_mark = config.bcolors.ENDC
        self.link_end_mark = '\N{INVISIBLE SEPARATOR}' #
        self.image_placeholder_char = '\N{HEAVY SPARKLE}' #\u2748
        self.use_automatic_links = config.USE_AUTOMATIC_LINKS  # covered in cli
        self.hide_strikethrough = False  # covered in cli
        self.mark_code = config.MARK_CODE
        self.pad_tables = config.PAD_TABLES  # covered in cli
        self.default_image_alt = config.DEFAULT_IMAGE_ALT  # covered in cli
        self.tag_callback = None

        if out is None:  # pragma: no cover
            self.out = self.outtextf
        else:  # pragma: no cover
            self.out = out

        # empty list to store output characters before they are "joined"
        self.outtextlist = []

        self.quiet = 0
        self.p_p = 0  # number of newline character to print before next output
        self.outcount = 0
        self.start = 1
        self.space = 0
        self.a = []
        self.astack = []
        self.maybe_automatic_link = None
        self.div_was_inline = False
        self.empty_link = False
        self.absolute_url_matcher = config.RE_ABSOLUTE_LINK
        self.acount = 0
        self.list = []
        self.blockquote = 0
        self.pre = 0
        self.startpre = 0
        self.code = False
        self.br_toggle = ''
        self.lastWasNL = 0
        self.lastWasList = False
        self.style = 0
        self.style_def = {}
        self.tag_stack = []
        self.emphasis = 0
        self.drop_white_space = 0
        self.inheader = False
        self.abbr_title = None  # current abbreviation definition
        self.abbr_data = None  # last inner HTML (for abbr being defined)
        self.abbr_list = {}  # stack of abbreviations to write later
        self.baseurl = baseurl
        self.stressed = False
        self.preceding_stressed = False
        self.preceding_data = None
        self.current_tag = None

    def feed(self, data):
        data = data.replace("</' + 'script>", "</ignore>")
        HTMLParser.HTMLParser.feed(self, data)

    def handle(self, data):
        self.feed(data)
        self.feed("")
        outtext = self.close()
        if self.pad_tables:
            outtext = pad_tables_in_text(outtext, columns=self.columns)

        # reduce >2 empty lines to only one empty line
        outtext = config.RE_MULTIPLE_EMPTY_LINES.sub('\n\n', outtext)
        # do the same for lines with only blockquote char and spaces
        outtext = config.RE_MULTIPLE_QUOTEEMPTY_LINES.sub('\g<QUOTE>', outtext)
        # remove trailing spaces
        outtext = config.RE_TRAILING_SPACES.sub('', outtext)
        fl = open('/tmp/test.txt', 'w')
        fl.write(outtext)
        fl.close()

        return outtext

    def outtextf(self, s):
        self.outtextlist.append(s)
        if s:
            self.lastWasNL = s[-1] == '\n'

    def close(self):
        HTMLParser.HTMLParser.close(self)

        self.pbr()
        self.o('', 0, 'end')

        outtext = nochr.join(self.outtextlist)

        nbsp = chr(name2cp('nbsp'))
        try:
            outtext = outtext.replace(unicode('&nbsp_place_holder;'), nbsp)
        except NameError:
            outtext = outtext.replace('&nbsp_place_holder;', nbsp)

        # Clear self.outtextlist to avoid memory leak of its content to
        # the next handling.
        self.outtextlist = []

        return outtext

    def handle_charref(self, c):
        self.handle_data(self.charref(c), True)

    def handle_entityref(self, c):
        self.handle_data(self.entityref(c), True)

    def handle_starttag(self, tag, attrs):
        self.handle_tag(tag, attrs, 1)

    def handle_endtag(self, tag):
        self.handle_tag(tag, None, 0)

    def previousIndex(self, attrs):
        """
        :type attrs: dict

        :returns: The index of certain set of attributes (of a link) in the
        self.a list. If the set of attributes is not found, returns None
        :rtype: int
        """
        if 'href' not in attrs:  # pragma: no cover
            return None
        i = -1
        for a in self.a:
            i += 1
            match = 0

            if 'href' in a and a['href'] == attrs['href']:
                if 'title' in a or 'title' in attrs:
                    if 'title' in a and \
                        'title' in attrs and \
                            a['title'] == attrs['title']:
                        match = True
                else:
                    match = True

            if match:
                return i

    def handle_emphasis(self, start, tag_style, parent_style):
        """
        Handles various text emphases
        """
        tag_emphasis = google_text_emphasis(tag_style)
        parent_emphasis = google_text_emphasis(parent_style)

        # handle Google's text emphasis
        strikethrough = 'line-through' in \
                        tag_emphasis and self.hide_strikethrough

        # google and others may mark a font's weight as `bold` or `700`
        bold = False
        for bold_marker in config.BOLD_TEXT_STYLE_VALUES:
            bold = (bold_marker in tag_emphasis
                    and bold_marker not in parent_emphasis)
            if bold:
                break

        italic = 'italic' in tag_emphasis and 'italic' not in parent_emphasis
        fixed = google_fixed_width_font(tag_style) and not \
            google_fixed_width_font(parent_style) and not self.pre

        if start:
            # crossed-out text must be handled before other attributes
            # in order not to output qualifiers unnecessarily
            if bold or italic or fixed:
                self.emphasis += 1
            if strikethrough:
                self.quiet += 1
            if italic:
                self.o(self.emphasis_mark_start)
                self.drop_white_space += 1
            if bold:
                self.o(self.strong_mark_start)
                self.drop_white_space += 1
            if fixed:
                self.o('`')
                self.drop_white_space += 1
                self.code = True
        else:
            if bold or italic or fixed:
                # there must not be whitespace before closing emphasis mark
                self.emphasis -= 1
                self.space = 0
            if fixed:
                if self.drop_white_space:
                    # empty emphasis, drop it
                    self.drop_white_space -= 1
                else:
                    self.o('`')
                self.code = False
            if bold:
                if self.drop_white_space:
                    # empty emphasis, drop it
                    self.drop_white_space -= 1
                else:
                    self.o(self.strong_mark_end)
            if italic:
                if self.drop_white_space:
                    # empty emphasis, drop it
                    self.drop_white_space -= 1
                else:
                    self.o(self.emphasis_mark_end)
            # space is only allowed after *all* emphasis marks
            if (bold or italic) and not self.emphasis:
                self.o(" ")
            if strikethrough:
                self.quiet -= 1

    def handle_tag(self, tag, attrs, start):
        self.current_tag = tag
        # attrs is None for endtags
        if attrs is None:
            attrs = {}
        else:
            attrs = dict(attrs)

        if self.tag_callback is not None:
            if self.tag_callback(self, tag, attrs, start) is True:
                return

        # first thing inside the anchor tag is another tag
        # that produces some output
        if (start and self.maybe_automatic_link is not None and
                tag not in ['p', 'div', 'style', 'dl', 'dt'] and
                (tag != "img")):
            #self.o("[")
            self.o(self.link_begin_mark)
            self.maybe_automatic_link = None
            self.empty_link = False

        if hn(tag):
            self.p()
            if start:
                self.inheader = True
                self.o(hn(tag) * "#" + ' ')
            else:
                self.inheader = False
                return  # prevent redundant emphasis marks on headers

        if tag in ['p', 'div']:
            if start and tag == 'div' and 'style' in attrs and 'display:inline' in attrs['style']:
                self.div_was_inline = True
            elif self.astack and tag == 'div':
                pass
            elif tag == 'div' and self.div_was_inline and not start:
                self.div_was_inline = False
            else:
                self.p(tag)

        if tag == "br" and start:
            quotechars = '>'*self.blockquote
            self.o("\n"+quotechars)

        if tag == "hr" and start:
            self.p()
            columns = self.columns or 10
            self.o("–"*columns)
            self.p()

        if tag in ["head", "style", 'script']:
            if start:
                self.quiet += 1
            else:
                self.quiet -= 1

        if tag == "style":
            if start:
                self.style += 1
            else:
                self.style -= 1

        if tag in ["body"]:
            self.quiet = 0  # sites like 9rules.com never close <head>

        if tag == "blockquote":
            if start:
                self.p()
                self.o('>', 0, 1)
                self.start = 1
                self.blockquote += 1
            else:
                self.blockquote -= 1
                self.p()

        def no_preceding_space(self):
            return (self.preceding_data
                    and config.RE_PRECEDING_SPACE.match(self.preceding_data[-1]))

        if tag in ['em', 'i']:
            if start:
                self.o(self.emphasis_mark_start)
                self.stressed = True
            else:
                self.o(self.emphasis_mark_end)

        if tag in ['u']:
            if start:
               self.o(self.underline_mark_start)
               self.stressed = True
            else:
                self.o(self.underline_mark_end)

        if tag in ['strong', 'b']:
            if start:
               self.o(self.strong_mark_start)
               self.stressed = True
            else:
                self.o(self.strong_mark_end)

        if tag in ['del', 'strike', 's']:
            strike = '~~'

            self.o(strike)
            if start:
                self.stressed = True

        if tag in ["code", "tt"] and not self.pre:
            self.o('`')  # TODO: `` `this` ``
            self.code = not self.code
        if tag == "abbr":
            if start:
                self.abbr_title = None
                self.abbr_data = ''
                if ('title' in attrs):
                    self.abbr_title = attrs['title']
            else:
                if self.abbr_title is not None:
                    self.abbr_list[self.abbr_data] = self.abbr_title
                    self.abbr_title = None
                self.abbr_data = ''

        def link_url(self, link, title=""):
            url = urlparse.urljoin(self.baseurl, link)
            title = ' "{0}"'.format(title) if title.strip() else ''
            self.o(self.link_end_mark + '({url}{title})'.format(url=url,
                                            title=title))

        if tag == "a":
            if start:
                if 'href' in attrs and \
                    attrs['href'] is not None and not \
                        (self.skip_internal_links and
                            attrs['href'].startswith('#')):
                    self.astack.append(attrs)
                    self.maybe_automatic_link = attrs['href']
                    self.empty_link = True
                else:
                    self.astack.append(None)
            else:
                if self.astack:
                    a = self.astack.pop()
                    if self.maybe_automatic_link and not self.empty_link:
                        self.maybe_automatic_link = None
                    elif a:
                        if self.empty_link:
                            #self.o("[")
                            self.o(self.link_begin_mark)
                            self.empty_link = False
                            self.maybe_automatic_link = None
                        if self.inline_links:
                            try:
                                title = a['title'] if a['title'] else ''
                            except KeyError:
                                link_url(self, a['href'], '')
                            else:
                                link_url(self, a['href'], title)
                        else:
                            i = self.previousIndex(a)
                            if i is not None:
                                a = self.a[i]
                            else:
                                self.acount += 1
                                a['count'] = self.acount
                                a['outcount'] = self.outcount
                                self.a.append(a)
                            self.o(self.link_end_mark + convert_superscript(a['count']))

        if tag == "img" and start:
            if 'src' in attrs:
                alt = attrs.get('alt') or self.default_image_alt
                # If we have images_to_alt, we discard the image itself,
                # considering only the alt text.
                if self.images_to_alt:
                    self.o(alt)
                else:
                    self.o(self.image_placeholder_char + alt )

        if tag == 'dl' and start:
            self.p()
        if tag == 'dt' and not start:
            self.pbr()
        if tag == 'dd' and start:
            self.o('    ')
        if tag == 'dd' and not start:
            self.pbr()

        if tag in ["ol", "ul"]:
            # Google Docs create sub lists as top level lists
            if (not self.list) and (not self.lastWasList):
                self.p()
            if start:
                list_style = tag
                numbering_start = list_numbering_start(attrs)
                self.list.append({
                    'name': list_style,
                    'num': numbering_start
                })
            else:
                if self.list:
                    self.list.pop()
                    if not self.list:
                        self.o('\n')
            self.lastWasList = True
        else:
            self.lastWasList = False

        if tag == 'li':
            self.pbr()
            if start:
                if self.list:
                    li = self.list[-1]
                else:
                    li = {'name': 'ul', 'num': 0}
                nest_count = len(self.list)
                # TODO: line up <ol><li>s > 9 correctly.
                self.o("  " * nest_count)
                if li['name'] == "ul":
                    self.o(self.ul_item_mark + " ")
                elif li['name'] == "ol":
                    li['num'] += 1
                    self.o(str(li['num']) + ". ")
                self.start = 1

        if tag in ["table", "tr", "td", "th"]:
            if self.ignore_tables:
                if tag == 'tr':
                    if start:
                        pass
                    else:
                        self.soft_br()
                else:
                    pass

            elif self.bypass_tables:
                if start:
                    self.soft_br()
                if tag in ["td", "th"]:
                    if start:
                        self.o('<{0}>\n\n'.format(tag))
                    else:
                        self.o('\n</{0}>'.format(tag))
                else:
                    if start:
                        self.o('<{0}>'.format(tag))
                    else:
                        self.o('</{0}>'.format(tag))

            else:
                if tag == "table":
                    if start:
                        self.table_start = True
                        if self.pad_tables:
                            self.o("<" + config.TABLE_MARKER_FOR_PAD + ">")
                            self.o("  \n")
                    else:
                        if self.pad_tables:
                            self.o("</" + config.TABLE_MARKER_FOR_PAD + ">")
                            self.o("  \n")
                if tag in ["td", "th"] and start:
                    if self.split_next_td:
                        self.o("│ ")
                    self.split_next_td = True

                if tag == "tr" and start:
                    self.td_count = 0
                if tag == "tr" and not start:
                    self.split_next_td = False
                    self.soft_br()
                if tag == "tr" and not start and self.table_start:
                    # Underline table header
                    self.o("│".join(["───"] * self.td_count))
                    self.soft_br()
                    self.table_start = False
                if tag in ["td", "th"] and start:
                    self.td_count += 1

        if tag == "pre":
            if start:
                self.startpre = 1
                self.pre = 1
            else:
                self.pre = 0
                if self.mark_code:
                    self.out("\n[/code]")
            self.p()

    # TODO: Add docstring for these one letter functions
    def pbr(self):
        "Pretty print has a line break"
        if self.p_p == 0:
            self.p_p = 1

    def p(self, tag='p'):
        "Set pretty print to 1 or 2 lines"
        if tag == 'div':
            self.p_p = 1
        else:
            self.p_p = 2

    def soft_br(self):
        "Soft breaks"
        self.pbr()
        self.br_toggle = '  '

    def o(self, data, puredata=0, force=0):
        """
        Deal with indentation and whitespace
        """
        if self.abbr_data is not None:
            self.abbr_data += data

        if not self.quiet:
            if puredata and not self.pre:
                # This is a very dangerous call ... it could mess up
                # all handling of &nbsp; when not handled properly
                # (see entityref)
                data = config.RE_SPACE_GENERAL.sub(' ', data)
                if data and data[0] == ' ':
                    self.space = 1
                    data = data[1:]
            if not data and not force:
                return

            if self.startpre:
                # self.out(" :") #TODO: not output when already one there
                if not data.startswith("\n") and not data.startswith("\r\n"):
                    # <pre>stuff...
                    data = "\n" + data
                if self.mark_code:
                    self.out("\n[code]")
                    self.p_p = 0

            bq = (">" * self.blockquote)
            if not (force and data and data[0] == ">") and self.blockquote:
                bq += " "

            if self.pre:
                if not self.list:
                    bq += "    "
                # else: list content is already partially indented
                for i in range(len(self.list)):
                    bq += "    "
                data = data.replace("\n", "\n" + bq)

            if self.startpre:
                self.startpre = 0
                if self.list:
                    # use existing initial indentation
                    data = data.lstrip("\n")

            if self.start:
                self.space = 0
                self.p_p = 0
                self.start = 0

            if force == 'end':
                # It's the end.
                self.p_p = 0
                self.out("\n")
                self.space = 0

            if self.p_p:
                self.out((self.br_toggle + '\n' + bq) * self.p_p)
                self.space = 0
                self.br_toggle = ''

            if self.space:
                if not self.lastWasNL and not self.blockquote:
                    self.out(' ')
                self.space = 0

            if self.a and ((self.p_p == 2 and self.links_each_paragraph) or
                           force == "end"):
                if force == "end":
                    self.out("\n")

                newa = []
                self.out('\n\n––––\n\n')
                for link in self.a:
                    if self.outcount > link['outcount']:
                        self.out(convert_superscript(link['count']) + " " +
                                 urlparse.urljoin(self.baseurl, link['href']))
                        if 'title' in link:
                            self.out(" (" + link['title'] + ")")
                        self.out("\n")
                    else:
                        newa.append(link)

                # Don't need an extra line when nothing was done.
                if self.a != newa:
                    self.out("\n")

                self.a = newa

            if self.abbr_list and force == "end":
                for abbr, definition in self.abbr_list.items():
                    self.out("  *[" + abbr + "]: " + definition + "\n")

            self.p_p = 0
            self.out(data)
            self.outcount += 1

    def handle_data(self, data, entity_char=False):
        if self.stressed:
            data = data.strip()
            self.stressed = False
            self.preceding_stressed = True
        elif (self.preceding_stressed
              and config.RE_NON_PUNCT.match(data[0])
              and not hn(self.current_tag)
              and self.current_tag not in ['a', 'code', 'pre']):
            # should match a letter or common punctuation
            data = ' ' + data
            self.preceding_stressed = False

        if self.style:
            self.style_def.update(dumb_css_parser(data))

        if self.maybe_automatic_link is not None:
            href = self.maybe_automatic_link
            if self.use_automatic_links:
                # massage href to remove mailto links
                href = href.replace('mailto:', '')
                # if href is a telephone number
                if href.startswith('tel:'):
                    href = data
                # data sometimes still contains spaces
                datacmp = data.strip()
                # href is equivalent to data if they only differ for a final '/'
                # check also if data is only missing the http/s part
                conditions = (href == datacmp,
                              href[7:] == datacmp,
                              href[8:] == datacmp,
                              href[:-1] == datacmp and href[-1] == '/',
                              href == datacmp[:-1] and datacmp[-1] == '/',
                              )
                if any(conditions):
                    self.o(data)
                    self.empty_link = False
                    return
                else:
                    #self.o("[")
                    self.o(self.link_begin_mark)
                    self.maybe_automatic_link = None
                    self.empty_link = False
            else:
                #self.o("[")
                self.o(self.link_begin_mark)
                self.maybe_automatic_link = None
                self.empty_link = False

        self.preceding_data = data
        self.o(data, 1)

    def unknown_decl(self, data):  # pragma: no cover
        # TODO: what is this doing here?
        pass

    def charref(self, name):
        if name[0] in ['x', 'X']:
            c = int(name[1:], 16)
        else:
            c = int(name)

        try:
            return chr(c)
        except ValueError:  # invalid unicode
            return ''

    def entityref(self, c):
        try:
            name2cp(c)
        except KeyError:
            return "&" + c + ';'
        else:
            return chr(name2cp(c))

    def replaceEntities(self, s):
        s = s.group(1)
        if s[0] == "#":
            return self.charref(s[1:])
        else:
            return self.entityref(s)




def html2text(html, baseurl=''):
    h = HTML2Text(baseurl=baseurl)

    return h.handle(html)




if __name__ == "__main__":
    from html2text.cli import main

    main()
