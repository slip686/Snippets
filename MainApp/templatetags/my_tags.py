from django import template

register = template.Library()


def br(val):
    if val == '\n':
        return '<br>'


def is_empty(value, alt):
    if value:
        return value
    return alt


register.filter('br', br)
register.filter('is_empty', is_empty)
