Djang0parser
============

Multifunctional html sanitizer with code highlighting and django integration

Installing
==========

In settings set VALID_TAGS and VALID_ATTRS, like:
 >>> VALID_TAGS = 'a strong img cut'
 >>> VALID_ATTRS = 'href src'

Add djang0parser to INSTALLED_APPS and run syncdb.

Usage
=====

For text sanitizing use:
 >>> from djang0parser.utils import parse
 >>> parse(text)

or:
 >>> parse(text, 'a b i img', 'src style')

For reverting changes use:
 >>> from djang0parser.utils import unparse
 >>> unparse(parsed_text)

For finding user mention use:
 >>> from djang0parser.utils import find_mentions
 >>> find_mentions(text)

For cut and full cut(fcut) use:
 >>> from djang0parser.utils import cut
 >>> preview, text = cut(full_text)
