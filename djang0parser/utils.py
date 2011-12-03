#!/usr/bin/python
# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import re
from BeautifulSoup import BeautifulSoup
from pygments import highlight
from pygments.lexers import get_lexer_by_name, PhpLexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
from djang0parser.models import Code
from django.conf import settings


VALID_TAGS = getattr(settings, 'VALID_TAGS', tuple())
VALID_ATTRS = getattr(settings, 'VALID_ATTRS', tuple())


class VeryBeautifulSoup(BeautifulSoup):
    """BeautifulSoup with attention to 'code' tag and Russian letters."""
    QUOTE_TAGS = BeautifulSoup.QUOTE_TAGS
    QUOTE_TAGS.update({
        "code": None
    })
    MARKUP_MASSAGE = BeautifulSoup.MARKUP_MASSAGE
    MARKUP_MASSAGE.append((re.compile(u'<(/?[а-яА-Я]+)>'),
                       lambda x: u"&lt" + x.group(1) + u"&gt;"))


def parse(value, valid_tags=VALID_TAGS, valid_attrs=VALID_ATTRS):
    """Cleans non-allowed HTML from the input.

    Keyword arguments:
    value -- String
    valid_tags -- String
    valid_attrs -- String

    Returns: String

    """
    valid_tags = valid_tags.split()
    valid_attrs = valid_attrs.split()
    value = value.replace('&quot;', '"').replace('&amp;', '&')
    soup = VeryBeautifulSoup(value)
    for tag in soup.findAll(True):
        if tag.name not in valid_tags:
            tag.hidden = True
        if tag.name == 'user':
            tag.replaceWith(
                '<a class="user_tag user_tag_%s" href="/user/%s/">%s</a>' %
                (tag.string, tag.string, tag.string)
            )
        if tag.name == 'quote':
            tag.replaceWith(
                '<div class="quote">%s</div>' %
                tag.__unicode__().replace('<quote>', '').replace('</quote>', '')
            )
        if tag.name == 'spoiler':
            tag.replaceWith(
                '<div class="spoiler">%s</div>' %
                tag.__unicode__().replace('<spoiler>', '').replace('</spoiler>', '')
            )
        for attr, val in tag.attrs:
            if attr in ('src', 'href') and val.find('javascript') == 0:
                tag.hidden = True
            if tag.name == 'code' and attr == 'lang':
                try:
                    lexer = get_lexer_by_name(val, encoding='utf-8', stripall=True, startinline=True)
                except ClassNotFound:
                    lexer = get_lexer_by_name('text')
                formatter = HtmlFormatter(
                    encoding='utf-8', style='colorful',
                    linenos='table', cssclass='highlight',
                    lineanchors="line"
                )
                code = tag.__unicode__()
                code_model = Code()
                code_model.code = code
                code_model.lang = val
                code_model.save()
                code = highlight(code, lexer, formatter)
                code = code.replace(
                    '<table class="highlighttable">',
                    '<table class="highlighttable" id="%d">' % code_model.id
                )
                tag.replaceWith(code)
            if tag.name == 'iframe' and attr == 'src' \
                 and (val.find('http://www.youtube.com/embed/') != 0
                 and val.find('http://player.vimeo.com/video/') != 0):
                tag.hidden = True
        tag.attrs = filter(lambda (attr, val): attr in valid_attrs, tag.attrs)
    return soup.renderContents().decode('utf8').replace('\n', '<br />')


def remove_code(value):
    """Remove code models from db

    Keyword arguments:
    value -- String

    Returns: None
    """
    soup = BeautifulSoup(value)
    for code in soup.findAll({'table': True, 'class=highlighttable': True}):
        try:
            Code.objects.get(id=int(code['id'])).delete()
        except Code.DoesNotExist:
            pass


def find_mentions(value):
    soup = BeautifulSoup(value)
    for user in soup.findAll({'user': True}):
        yield user.string


def unparse(value):
    """Revert parser activity

    Keyword arguments:
    value -- String

    Returns: String
    """
    value = value.replace('<br />', '\n')
    soup = BeautifulSoup(value)
    for code in soup.findAll('table', {'class': 'highlighttable'}):
        try:
            new_code = Code.objects.get(id=int(code['id']))
            code.replaceWith('<code lang="%s">%s</code>' % (new_code.lang, new_code.code))
        except Code.DoesNotExist:
            pass
    for user in soup.findAll('a'):
        try:
            if 'user_tag' in user['class'].split(' '):
                user.replaceWith("<user>%s</user>" % user.string)
        except Exception:
            pass
    for quote in soup.findAll('div', {'class': 'quote'}):
        text = quote.__unicode__().replace('<div class="quote">', '')
        text = ''.join(text.split('</div>')[:-1])
        quote.replaceWith("<quote>%s</quote>" % text)
    for quote in soup.findAll('div', {'class': 'spoiler'}):
        text = quote.__unicode__().replace('<div class="spoiler">', '')
        text = ''.join(text.split('</div>')[:-1])
        quote.replaceWith("<spoiler>%s</spoiler>" % text)
    return soup.renderContents().decode('utf8').replace('</fcut>', '').replace('</cut>', '')


def cut(text):
    """Cut text.

    Keyword arguments:
    text -- String

    Returns: String

    """
    text = text.replace('&lt;fcut&gt;', '<fcut>').replace('&lt;cut&gt;', '<cut>')
    cutted = text.split('<cut>')
    if len(cutted) == 2:
        return cutted[0], text
    cutted = text.split('<fcut>')
    if len(cutted) == 2:
        return cutted[0], '<fcut>' + cutted[1]
    else:
        return text, text
