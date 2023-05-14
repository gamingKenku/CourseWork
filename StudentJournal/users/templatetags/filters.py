from django.template.defaulttags import register
from django import template
import datetime

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='has_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter
def hm_format_time(value):
    if type(value) == str:
        value = datetime.time.fromisoformat(value)
    return datetime.time.strftime(value, '%H:%M')
