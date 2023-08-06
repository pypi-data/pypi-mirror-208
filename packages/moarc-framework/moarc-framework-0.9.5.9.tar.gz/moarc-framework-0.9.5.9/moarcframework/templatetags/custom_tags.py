import unidecode
from django import template

register = template.Library()


@register.filter(name='get_obj_attr')
def get_obj_attr(obj, attr):
    value = getattr(obj, attr)
    if value is None:
        return ''
    return value


@register.filter(name='encode')
def encode(attr):
    return unidecode.unidecode(attr)
