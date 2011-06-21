# from http://open.e-scribe.com/browser/python/django/apps/protowiki/templatetags/wikitags.py
# copyright Paul Bissex, MIT license
import re
from django.core.exceptions import ObjectDoesNotExist
from django.template import Library, Node, Variable
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from wakawaka.models import WikiPage
from wakawaka.urls import WIKI_WORD
import urllib 
from django.template.defaultfilters import slugify

register = Library()

WIKI_WORDS_REGEX = re.compile(WIKI_WORD)

def replace_wikiwords(value, group=None):
    def replace_wikiword(m):
        text = m.group(1)
        slug = slugify(text)
        try:
            page = WikiPage.objects.get(slug=slug)
            kwargs = {
                'slug' : urllib.quote(slug.encode('utf-8')), 
            }
            if group:
                url = group.content_bridge.reverse('wakawaka_page', group, kwargs=kwargs)
            else:
                url = reverse('wakawaka_page', kwargs=kwargs)
            return r'<a href="%s">%s</a>' % (url, text)
        except ObjectDoesNotExist:
            kwargs = {
                'slug': slug,
            }
            if group:
                url = group.content_bridge.reverse('wakawaka_edit', group, kwargs=kwargs)
            else:
                url = reverse('wakawaka_edit', kwargs=kwargs)
            return r'<a class="doesnotexist" href="%s">%s</a>' % (url, text)
    return mark_safe(WIKI_WORDS_REGEX.sub(replace_wikiword, value))

@register.filter
def wikify(value):
    """Makes WikiWords"""
    return replace_wikiwords(value)


class WikifyContentNode(Node):
    def __init__(self, content_expr, group_var):
        self.content_expr = content_expr
        self.group_var = Variable(group_var)
    
    def render(self, context):
        content = self.content_expr.resolve(context)
        group = self.group_var.resolve(context)
        return replace_wikiwords(content, group)

@register.tag
def wikify_content(parser, token):
    bits = token.split_contents()
    try:
        group_var = bits[2]
    except IndexError:
        group_var = None
    return WikifyContentNode(parser.compile_filter(bits[1]), group_var)
