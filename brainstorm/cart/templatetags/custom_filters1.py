# custom_filters.py
from django import template

register = template.Library()


@register.filter
def get_range(value):
    return range(1, value + 1)

@register.filter
def get_range(value):
    return range(value)

@register.filter
def get_inverse_range(value):
    return range(5 - value)
