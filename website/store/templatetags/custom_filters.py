# custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_last_segment(value):
    return value.split('/')[-1]

@register.filter
def round_to_integer(value):
    return round(value)