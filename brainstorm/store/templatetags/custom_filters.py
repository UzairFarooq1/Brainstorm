# custom_filters.py
from django import template
import math

register = template.Library()

@register.filter
def get_range(value):
    return range(value)

@register.filter
def get_inverse_range(value):
    return range(5 - value)

@register.filter
def star_rating(avg_rating):
    integer_part = int(avg_rating)
    decimal_part = avg_rating - integer_part
    stars = ['fas fa-star text-warning'] * integer_part
    if decimal_part >= 0.25:
        stars.append('fas fa-star-half-alt text-warning')
    stars += ['far fa-star text-warning'] * (5 - len(stars))
    return stars
