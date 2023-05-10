from django.shortcuts import render
from scheduling.schedule_creator import BellSchedule, WeekSchedule, Lesson
from .forms import LessonSheduleForm
from django.forms import formset_factory

def create_schedule(request):
    context = {}

    if request.method == "POST":
        pass

    week = WeekSchedule()
    LessonScheduleFormset = formset_factory(LessonSheduleForm, extra=12)

    for day in week.schedule.keys():
        formset = LessonScheduleFormset(prefix=day)

        i = 0
        for form in formset:
            form.fields["start_time"].initial = week.schedule[day][i].start_time
            i += 1

        context[f"{day}_lesson_form"] = formset

    return render(request, "create_schedule.html", context)