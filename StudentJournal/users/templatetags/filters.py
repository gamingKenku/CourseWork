from django.template.defaulttags import register
from django import template
import datetime
from scheduling.models import LessonSchedule

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_discipline(dictionary, key):
    return dictionary.get(key).discipline_teacher.discipline


@register.filter(name='has_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter
def hm_format_time(value):
    print(type(value))
    if type(value) == str:
        value = datetime.time.fromisoformat(value)
    return datetime.time.strftime(value, '%H:%M')
