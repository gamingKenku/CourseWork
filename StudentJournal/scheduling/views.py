from django.shortcuts import render, get_object_or_404
from scheduling.schedule_creator import BellSchedule, WeekScheduleCreator, Lesson, QuarterSchedule, WeekClassSchedule
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest
from .forms import LessonSheduleForm, LessonBellScheduleForm, QuartersScheduleForm, ClassPicker, DisciplineNamePicker, TermPicker
from .models import LessonSchedule
from django.forms import formset_factory
from users.models import ClassCode, AppUser, DisciplineTeacher, ClassStudent, DisciplineName
from django.http import JsonResponse
from django.db.models import Q
import datetime


def create_schedule(request, class_id):
    context = {}

    class_code = ClassCode.objects.get(id=class_id)
    week = WeekScheduleCreator(class_code=class_code)
    LessonScheduleFormset = formset_factory(LessonSheduleForm, extra=12)

    if request.method == "POST":
        formsets_dict = {}
        formset_valid = True
        for day in week.schedule.keys():
            formset = LessonScheduleFormset(request.POST, prefix=day)

            if not formset.is_valid():
                formset_valid = False

            formsets_dict[f"{day}_lesson_form"] = formset

        if not formset_valid:
            context.update(formsets_dict)
        else:
            term_number = int(request.POST["term_select"]) - 1
            week = WeekScheduleCreator(class_code=class_code, week_formset_dict=formsets_dict)
            week.reset_and_generate_schedule_records(term_number)
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
    
    context["class_code"] = class_code
    return render(request, "create_schedule.html", context)


def get_teachers_for_discipline(request, discipline_id):
    discipline_teacher_records = DisciplineTeacher.objects.filter(discipline=discipline_id)
    teacher_list = [{'id': discipline_teacher_record.teacher.id, 'name': discipline_teacher_record.teacher.__str__()} for discipline_teacher_record in discipline_teacher_records]
    return JsonResponse({'teachers': teacher_list})


def edit_schedule(request, class_id):
    pass


def reset_schedule(request, class_id):
    pass


def bell_quarter_edit(request):
    context = {}

    LessonBellScheduleFormset = formset_factory(LessonBellScheduleForm, extra=0)
    QuartersScheduleFormset = formset_factory(QuartersScheduleForm, extra=0)

    if request.method == "POST":
        bell_schedule_formset = LessonBellScheduleFormset(request.POST, prefix="bell")
        quarter_schedule_formset = QuartersScheduleFormset(request.POST, prefix="quarter")
        if bell_schedule_formset.is_valid() and quarter_schedule_formset.is_valid():
            bell_schedule_formset_data = []

            for form in bell_schedule_formset:
                form_data = {}
                for field_name, field_value in form.cleaned_data.items():
                    form_data[field_name] = field_value
                bell_schedule_formset_data.append(form_data)

            quarter_schedule_formset_data = []

            for form in quarter_schedule_formset:
                form_data = {}
                for field_name, field_value in form.cleaned_data.items():
                    form_data[field_name] = field_value        
                quarter_schedule_formset_data.append(form_data)

            BellSchedule.save_to_file(bell_schedule_formset_data)
            QuarterSchedule.save_to_file(quarter_schedule_formset_data)
            BellSchedule.initialise_from_file()
            QuarterSchedule.initialise_from_file()

            return HttpResponseRedirect("/")
        else:
            print(bell_schedule_formset.errors)
            print(bell_schedule_formset.non_form_errors())
            print(quarter_schedule_formset.errors)
            print(quarter_schedule_formset.non_form_errors())
    else:
        initial_bell_schedule = list(BellSchedule.bell_schedule)
        initial_quarter_schedule = list(QuarterSchedule.quarter_schedule)
        bell_schedule_formset = LessonBellScheduleFormset(prefix="bell", initial=initial_bell_schedule)
        quarter_schedule_formset = QuartersScheduleFormset(prefix="quarter", initial=initial_quarter_schedule)

    context["bell_formset"] = bell_schedule_formset
    context["quarter_formset"] = quarter_schedule_formset
    return render(request, "bell_quarter_edit.html", context)


def schedule_menu(request):
    context = {
        "class_picker": ClassPicker(),
        "discipline_picker": DisciplineNamePicker(),
        "term_picker": TermPicker(),
    }
    return render(request, "schedule_menu.html", context)


def student_journal(request, week_start_date, week_end_date):
    user_class_code = get_object_or_404(ClassStudent, student=request.user.id).class_code

    try:
        week_start_date = datetime.date.fromisoformat(week_start_date)
        week_end_date = datetime.date.fromisoformat(week_end_date)
    except ValueError:
        return HttpResponseBadRequest("Ошибка в обработке даты.")
    
    try:
        schedule_dict = WeekClassSchedule.get_schedule_as_context(week_start_date, week_end_date, user_class_code)
    except ValueError:
        raise Http404("Учебная неделя не найдена.")
    
    context = {}
    context.update(schedule_dict)

    context["current_week_start_date"] = week_start_date.strftime("%d.%m.%Y")
    context["current_week_end_date"] = week_end_date.strftime("%d.%m.%Y")
    context["next_week_start_date"] = (week_start_date + datetime.timedelta(days=7)).isoformat()
    context["next_week_end_date"] = (week_end_date + datetime.timedelta(days=7)).isoformat()
    context["prev_week_start_date"] = (week_start_date - datetime.timedelta(days=7)).isoformat()
    context["prev_week_end_date"] = (week_end_date - datetime.timedelta(days=7)).isoformat()

    return render(request, "student_journal.html", context)


def class_journal(request, class_id, discipline_id, term):
    context = {}

    class_code = get_object_or_404(ClassCode, id=class_id)
    discipline = get_object_or_404(DisciplineName, id=discipline_id)
    students_records = ClassStudent.objects.filter(class_code=class_code)
    int_term = int(term) - 1

    term_start_date = QuarterSchedule.quarter_schedule[int_term]["start_date"]
    term_end_date = QuarterSchedule.quarter_schedule[int_term]["end_date"] + datetime.timedelta(days=1)

    lesson_records = LessonSchedule.objects.filter(Q(lesson_holding_datetime_start__gte=term_start_date) & Q(lesson_holding_datetime_start__lte=term_end_date) & Q(discipline_teacher__discipline=discipline) & Q(class_code=class_code))

    context.update({
        "students_records": students_records,
        "discipline": discipline,
        "class_code": class_code,
        "lesson_records": lesson_records,
        "term": term
    })

    return render(request, "class_journal.html", context)


