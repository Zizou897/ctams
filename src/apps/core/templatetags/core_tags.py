from django import template
from config.constants import SECTORS

register = template.Library()


@register.simple_tag
def company_phone():
    return '07 04 73 04 99'


@register.simple_tag
def company_email():
    return 'commercial@ctams.net'


@register.simple_tag
def get_sectors():
    return SECTORS
