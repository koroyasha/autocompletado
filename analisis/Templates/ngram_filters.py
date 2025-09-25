from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def get_item(dictionary, key):
    """Filtro para obtener un valor de un diccionario usando una clave"""
    return dictionary.get(key, {})

@register.filter
def dictsort_by_probabilidad(dictionary, reverse=True):
    """Filtro para ordenar un diccionario por probabilidad"""
    if not dictionary:
        return []
    
    items = dictionary.items()
    if reverse:
        return sorted(items, key=lambda x: x[1].get('probabilidad', 0), reverse=True)
    else:
        return sorted(items, key=lambda x: x[1].get('probabilidad', 0))