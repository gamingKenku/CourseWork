from django.template.defaulttags import register
from django import template
import datetime
from scheduling.models import LessonSchedule
from scheduling.schedule_creator import QuarterSchedule

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_discipline(dictionary, key):
    return dictionary.get(key).discipline_teacher.discipline


@register.filter
def get_grade(lesson):
    try:
        grade = lesson.lesson_to_results.get().grade
    except:
        grade = None
    return grade


@register.filter
def get_nonatt_reason(lesson):
    try:
        reason = lesson.lesson_to_results.get().non_attendance_reason
    except:
        reason = None
    return reason


@register.filter
def get_homework(dictionary, key):
    return dictionary.get(key).homework


@register.filter
def get_id(dictionary, key):
    return dictionary.get(key).id


@register.filter(name='has_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter
def hm_format_time(value):
    if type(value) == str:
        value = datetime.time.fromisoformat(value)
    return datetime.time.strftime(value, '%H:%M')


@register.simple_tag
def current_monday():
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    return monday.strftime('%Y-%m-%d')


@register.simple_tag
def current_sunday():
    today = datetime.date.today()
    sunday = today + datetime.timedelta(days=(6 - today.weekday()))
    return sunday.strftime('%Y-%m-%d')


@register.simple_tag
def start_of_term(term):
    term_start = QuarterSchedule.quarter_schedule[term]["start_date"]

    monday = term_start - datetime.timedelta(days=term_start.weekday())
    sunday = term_start + datetime.timedelta(days=(6 - term_start.weekday()))
    
    return monday.strftime('%Y-%m-%d') + "/" + sunday.strftime('%Y-%m-%d') + "/"
