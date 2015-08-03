from django import template

register = template.Library()

@register.filter('percentage')
def percentage(value):
    return "{0:.2%}".format(value)
