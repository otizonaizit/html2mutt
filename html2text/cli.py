import io
import optparse
import os
import sys
import warnings

from html2text import HTML2Text, config, __version__

def main():
    baseurl = ''
    p = optparse.OptionParser(
        '%prog [filename]',
        version='%prog ' + ".".join(map(str, __version__))
    )
    p.add_option(
        "--columns",
        dest="columns",
        action="store",
        type="int",
        default=0,
        help="columns"
    )
    p.add_option(
        "--encoding",
        dest="encoding",
        action="store",
        type="string",
        default="utf-8",
        help="input encoding"
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

    encoding = options.encoding
    if encoding == 'us-ascii':
        encoding = 'utf-8'

    try:
        if len(args) == 0:
            data = io.TextIOWrapper(sys.stdin.buffer,
                                    encoding=encoding,
                                    errors=options.decode_errors).read()
        elif len(args) == 1:
            data = open(args[0], 'rt', encoding=encoding,
                                       errors=options.decode_errors).read()
        else:
            p.error('Too many arguments')
    except UnicodeDecodeError as err:
        sys.stderr.write('Decoding error! Use --decode-errors=ignore!')
        raise err

    # handle columns
    if not options.columns:
        # try to read columns from enviroment
        try:
            columns = int(os.environ['COLUMNS'])-1
        except KeyError:
            columns = 79
    else:
        columns = int(options.columns) -1

    # remove tags that we can't parse properly beforehand
    # word break opportunity tag
    data = data.replace('<wbr>', '')
    data = data.replace('<wbr class="">', '')
    # zero-width space
    data = data.replace('\u200b', '')

    h = HTML2Text(baseurl=baseurl)


    h.columns = options.columns
    h.inline_links = options.inline_links
    h.pad_tables = options.pad_tables

    sys.stdout.buffer.write(h.handle(data).encode('utf-8'))
