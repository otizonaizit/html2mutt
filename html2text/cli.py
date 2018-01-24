import io
import optparse
import sys
import warnings

from html2text.compat import urllib
from html2text import HTML2Text, config, __version__
from html2text.utils import wrapwrite, wrap_read


def main():
    baseurl = ''
    p = optparse.OptionParser(
        '%prog [(filename|url) [encoding] [columns]]',
        version='%prog ' + ".".join(map(str, __version__))
    )
    p.add_option(
        "--pad-tables",
        dest="pad_tables",
        action="store_true",
        default=config.PAD_TABLES,
        help="pad the cells to equal column width in tables"
    )
    p.add_option(
        "--reference-links",
        dest="inline_links",
        action="store_false",
        default=config.INLINE_LINKS,
        help="use reference style links instead of inline links"
    )
    p.add_option(
        "--decode-errors",
        dest="decode_errors",
        action="store",
        type="string",
        default=config.DECODE_ERRORS,
        help="What to do in case of decode errors.'ignore', 'strict' and "
             "'replace' are acceptable values"
    )
    (options, args) = p.parse_args()

    # process input
    encoding = None
    columns = None
    if len(args) > 1:
        encoding = args[1]
    if len(args) > 2:
        columns = int(args[2])-1
    if len(args) > 3:
        p.error('Too many arguments')

    # just be safe
    if encoding == 'us-ascii':
        encoding = 'utf-8'

    if len(args) > 0:  # pragma: no cover
        file_ = args[0]

        if file_ == '-':
            data = io.TextIOWrapper(sys.stdin.buffer, encoding=encoding).read()
        else:
            data = open(file_, 'rb').read()

        if encoding is None:
            try:
                from chardet import detect
            except ImportError:
                def detect(x):
                    return {'encoding': 'utf-8'}
            encoding = detect(data)['encoding']
    else:
        data = wrap_read()

    if hasattr(data, 'decode'):
        try:
            try:
                data = data.decode(encoding, errors=options.decode_errors)
            except TypeError:
                # python 2.6.x does not have the errors option
                data = data.decode(encoding)
        except UnicodeDecodeError as err:
            bcolors = config.bcolors
            warning = bcolors.WARNING + "Warning:" + bcolors.ENDC
            warning += ' Use the ' + bcolors.OKGREEN
            warning += '--decode-errors=ignore' + bcolors.ENDC + 'flag.'
            print(warning)
            raise err

    # remove tags that we can't parse properly beforehand
    # word break opportunity tag
    data = data.replace('<wbr>', '')
    data = data.replace('<wbr class="">', '')
    # zero-width space
    data = data.replace('\u200b', '')

    h = HTML2Text(baseurl=baseurl)

    h.ul_item_mark = '-'

    h.columns = columns
    h.inline_links = options.inline_links
    h.pad_tables = options.pad_tables

    wrapwrite(h.handle(data))
