from django.shortcuts import render
from scheduling.schedule_creator import BellSchedule, WeekSchedule, Lesson
from django.http import HttpResponseRedirect
from .forms import LessonSheduleForm
from django.forms import formset_factory


def create_schedule(request):
    context = {}

    week = WeekSchedule()
    LessonScheduleFormset = formset_factory(LessonSheduleForm, extra=12)

    if request.method == "POST":
        formsets_dict = {}
        formset_valid = True
        for day in week.schedule.keys():
            formset = LessonScheduleFormset(request.POST, prefix=day)
            if not formset.is_valid():
                print("invalid")
                print(formset.errors)
                print(formset.non_form_errors())
                formset_valid = False
            else:
                print("valid")

            formsets_dict[f"{day}_lesson_form"] = formset

        if not formset_valid:
            context.update(formsets_dict)
        else:
            return HttpResponseRedirect("/")
    else:
        for day in week.schedule.keys():
            formset = LessonScheduleFormset(prefix=day)

            i = 0
            for form in formset:
                form.fields["start_time"].initial = week.schedule[day][i].start_time
                form.fields["end_time"].initial = week.schedule[day][i].end_time
                i += 1

            context[f"{day}_lesson_form"] = formset
    return render(request, "create_schedule.html", context)
