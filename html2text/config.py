import re

# Marker to use for marking tables for padding post processing
TABLE_MARKER_FOR_PAD = "special_marker_for_table_padding"

# Put the links after each paragraph instead of at the end.
LINKS_EACH_PARAGRAPH = 0

# Don't show internal links (href="#local-anchor") -- corresponding link
# targets won't be visible in the plain text file anyway.
SKIP_INTERNAL_LINKS = True

# Use inline, rather than reference, formatting for images and links
INLINE_LINKS = False

# Values Google and others may use to indicate bold text
BOLD_TEXT_STYLE_VALUES = ('bold', '700', '800', '900')

MARK_CODE = False
DECODE_ERRORS = 'strict'
PAD_TABLES = True

# Convert links with same href and text to <href> format
# if they are absolute links
USE_AUTOMATIC_LINKS = True

# For checking space-only lines on line 771
RE_SPACE = re.compile(r'\s\+')
RE_SPACE_GENERAL = re.compile(r'\s+')
RE_TRAILING_SPACES = re.compile(r'[^\S\r\n]+$', re.MULTILINE)
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

# Ignore table-related tags (table, th, td, tr) while keeping rows
IGNORE_TABLES = False


class bcolors:  # pragma: no cover
    HEADER = '\033[35m'
    OKBLUE = '\033[34m'
    OKGREEN = '\033[32m'
    WARNING = '\033[33m'
    FAIL = '\033[31m'
    YELLOW = '\033[33m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

