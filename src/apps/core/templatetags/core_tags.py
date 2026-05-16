from django import template
from config.constants import SECTORS

register = template.Library()


@register.simple_tag
def company_phone():
    return '07 77 90 68 45'


@register.simple_tag
def company_email():
    return 'Sasava221@gmail.com'


@register.simple_tag
def get_sectors():
    return SECTORS
