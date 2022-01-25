from django import template
from django.template.defaultfilters import stringfilter

from prospector.dataformats import phone_numbers

register = template.Library()


@register.filter
@stringfilter
def phonenumber(value):
    return phone_numbers.format(value)
