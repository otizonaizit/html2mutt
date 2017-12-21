import re

# Use Unicode characters instead of their ascii pseudo-replacements
UNICODE_SNOB = 1

# Marker to use for marking tables for padding post processing
TABLE_MARKER_FOR_PAD = "special_marker_for_table_padding"
# Escape all special characters.  Output is less readable, but avoids
# corner case formatting issues.
ESCAPE_SNOB = 0

# Put the links after each paragraph instead of at the end.
LINKS_EACH_PARAGRAPH = 0

# Wrap long lines at position. 0 for no wrapping. (Requires Python 2.3.)
BODY_WIDTH = 0

# Don't show internal links (href="#local-anchor") -- corresponding link
# targets won't be visible in the plain text file anyway.
SKIP_INTERNAL_LINKS = True

# Use inline, rather than reference, formatting for images and links
INLINE_LINKS = True

# Protect links from line breaks surrounding them with angle brackets (in
# addition to their square brackets)
PROTECT_LINKS = False
# WRAP_LINKS = True
WRAP_LINKS = False

# Number of pixels Google indents nested lists
GOOGLE_LIST_INDENT = 36

# Values Google and others may use to indicate bold text
BOLD_TEXT_STYLE_VALUES = ('bold', '700', '800', '900')

IGNORE_ANCHORS = False
IGNORE_IMAGES = True
IMAGES_TO_ALT = False
IMAGES_WITH_SIZE = False
IGNORE_EMPHASIS = False
MARK_CODE = False
DECODE_ERRORS = 'strict'
DEFAULT_IMAGE_ALT = ''
PAD_TABLES = False

# Convert links with same href and text to <href> format
# if they are absolute links
USE_AUTOMATIC_LINKS = True

# For checking space-only lines on line 771
RE_SPACE = re.compile(r'\s\+')
RE_SPACE_GENERAL = re.compile(r'\s+')
RE_MULTIPLE_EMPTY_LINES = re.compile(r'\n\s*\n')
RE_MULTIPLE_QUOTEEMPTY_LINES = re.compile(r'(?P<QUOTE>\>+ *\n){2,}')
RE_PRECEDING_SPACE = re.compile(r'[^\s]')
RE_NON_PUNCT = re.compile(r'[^\s.!?]')

RE_UNESCAPE = re.compile(r"&(#?[xX]?(?:[0-9a-fA-F]+|\w{1,8}));")
RE_ORDERED_LIST_MATCHER = re.compile(r'\d+\.\s')
RE_UNORDERED_LIST_MATCHER = re.compile(r'[-\*\+]\s')

# to find links in the text
RE_LINK = re.compile(r"(\[.*?\] ?\(.*?\))|(\[.*?\]:.*?)")
RE_ABSOLUTE_LINK = re.compile(r'^[a-zA-Z+]+://')

UNIFIABLE = {
    'rsquo': "'",
    'lsquo': "'",
    'rdquo': '"',
    'ldquo': '"',
    'copy': '(C)',
    'mdash': '--',
    'nbsp': ' ',
    'rarr': '->',
    'larr': '<-',
    'middot': '*',
    'ndash': '-',
    'oelig': 'oe',
    'aelig': 'ae',
    'agrave': 'a',
    'aacute': 'a',
    'acirc': 'a',
    'atilde': 'a',
    'auml': 'a',
    'aring': 'a',
    'egrave': 'e',
    'eacute': 'e',
    'ecirc': 'e',
    'euml': 'e',
    'igrave': 'i',
    'iacute': 'i',
    'icirc': 'i',
    'iuml': 'i',
    'ograve': 'o',
    'oacute': 'o',
    'ocirc': 'o',
    'otilde': 'o',
    'ouml': 'o',
    'ugrave': 'u',
    'uacute': 'u',
    'ucirc': 'u',
    'uuml': 'u',
    'lrm': '',
    'rlm': ''
}

# Format tables in HTML rather than Markdown syntax
BYPASS_TABLES = False
# Ignore table-related tags (table, th, td, tr) while keeping rows
IGNORE_TABLES = True


# Use a single line break after a block element rather than two line breaks.
# NOTE: Requires body width setting to be 0.
SINGLE_LINE_BREAK = False

class bcolors:  # pragma: no cover
    HEADER = '\033[35m'
    OKBLUE = '\033[34m'
    OKGREEN = '\033[32m'
    WARNING = '\033[33m'
    FAIL = '\033[31m'
    YELLOW = '\033[33m'
    ITALICS = '\033[3m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

