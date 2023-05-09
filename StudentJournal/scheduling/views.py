from django.shortcuts import render
from scheduling.schedule_creator import BellSchedule, WeekSchedule, Lesson
from .forms import LessonDisciplineTeacherForm

def create_schedule(request):
    context = {}

    if request.method == "POST":
        pass

    week = WeekSchedule()

    for day in week.schedule.keys():
        for i in range(0, 12):
            context[f"{day}-{i}-lesson_form"] = LessonDisciplineTeacherForm(prefix=f"{day}-{i}-lesson_form")
            
    return render(request, "")