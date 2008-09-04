"""
tagdepth metric

Compares pages analyzing a predefined set of (relevant)
tags and the depth where they appear in the page markup document. 

Requires ResponseSoup extension enabled.
"""

from __future__ import division

from BeautifulSoup import Tag

relevant_tags = set(['div', 'table', 'td', 'tr', 'h1'])

def get_symbol_dict(node, tags=(), depth=1):
    symdict = {}
    for tag in node:
        if isinstance(tag, Tag) and tag.name in tags:
            symbol = "%d%s" % (depth, str(tag.name))
            symdict[symbol] = symdict.setdefault(symbol, 0) + 1
            symdict.update(get_symbol_dict(tag, tags, depth+1))
    return symdict

def simhash(response):
    soup = response.soup
    symdict = get_symbol_dict(response.soup.find('body'), relevant_tags)
    return set(symdict.keys())

def compare(sh1, sh2):
    return len(sh1 & sh2) / len(sh1 | sh2)