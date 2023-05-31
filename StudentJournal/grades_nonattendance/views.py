import datetime
import numpy as np
import pandas as pd
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from scheduling.forms import LessonMaterialUploadForm
from scheduling.models import LessonSchedule
from scheduling.schedule_creator import QuarterSchedule
from users.models import ClassCode, ClassStudent, DisciplineName, AppUser
from .models import LessonResults;
from scheduling.schedule_creator import QuarterSchedule
from django.contrib.auth.decorators import login_required, permission_required
from .student_reports import get_grades_dataframe, get_grades_nonatt_as_dict, get_nonatt_dataframe, get_week_numbers, grades_nonatt_is_valid


@login_required(login_url="/login/")
@permission_required("scheduling.can_view_class_journal")
def class_journal(request, class_id, discipline_id, term):
    if int(term) < 1 or int(term) > 4:
        raise Http404("Четверть не найдена.")

    context = {}

    GRADES = (
        "1", "2", "3", "4", "5"
    )

    class_code = get_object_or_404(ClassCode, id=class_id)
    discipline = get_object_or_404(DisciplineName, id=discipline_id)
    students_records = ClassStudent.objects.filter(class_code=class_code)
    int_term = int(term) - 1
    existing_grades_nonatt = get_grades_nonatt_as_dict(students_records, int_term)

    if request.method == "POST":
        post_data = request.POST.copy()
        del post_data["csrfmiddlewaretoken"]

        if grades_nonatt_is_valid(post_data):
            for grade_nonatt in post_data.items():
                data = grade_nonatt[0].split("-")

                student = AppUser.objects.get(id=int(data[-2]))
                lesson = LessonSchedule.objects.get(id=int(data[-1]))

                if grade_nonatt[1] == "DE":
                    LessonResults.objects.filter(student=student, lesson=lesson).delete()
                elif grade_nonatt[1] in GRADES:
                    grade = int(grade_nonatt[1])
                    LessonResults.objects.update_or_create(student=student, lesson=lesson, defaults={"grade": grade, "non_attendance_reason": None})
                else:
                    non_attendance_reason = grade_nonatt[1]
                    LessonResults.objects.update_or_create(student=student, lesson=lesson, defaults={"non_attendance_reason": non_attendance_reason, "grade": None})

            return HttpResponseRedirect("/")
        else:
            existing_grades_nonatt = list(post_data.items())
            context.update({"existing_grades_nonatt": existing_grades_nonatt})
    else:
        existing_grades_nonatt = list(existing_grades_nonatt.items())
        context.update({"existing_grades_nonatt": existing_grades_nonatt})

    lesson_material_form = LessonMaterialUploadForm()

    term_start_date = QuarterSchedule.quarter_schedule[int_term]["start_date"]
    term_end_date = QuarterSchedule.quarter_schedule[int_term]["end_date"] + datetime.timedelta(days=1)

    lesson_records = LessonSchedule.objects.filter(
        Q(lesson_holding_datetime_start__gte=term_start_date) & 
        Q(lesson_holding_datetime_start__lte=term_end_date) & 
        Q(discipline_teacher__discipline=discipline) & 
        Q(class_code=class_code)
        )

    context.update({
        "students_records": students_records,
        "discipline": discipline,
        "class_code": class_code,
        "lesson_records": lesson_records,
        "term": term,
        "lesson_material_form": lesson_material_form
    })

    return render(request, "class_journal.html", context)


@login_required(login_url="/login/")
@permission_required("grades_nonattendance.view_lessonresults")
def nonatt_report(request, student_id, term):
    if int(term) < 1 or int(term) > 4:
        raise Http404("Четверть не найдена.")
    
    term_start_date = QuarterSchedule.quarter_schedule[int(term - 1)]["start_date"]
    term_end_date = QuarterSchedule.quarter_schedule[int(term - 1)]["end_date"] + datetime.timedelta(days=1)

    student = get_object_or_404(AppUser, pk=student_id)

    nonatt_dataframe = get_nonatt_dataframe(term_start_date, term_end_date, student)

    context = {
        "student": student,
        "term": term
        }

    if len(nonatt_dataframe.index) == 1:
        context["dataframe_no_index_flag"] = True
        return render(request, "nonatt_report.html", context)

    nonatt_html = nonatt_dataframe.to_html(
        classes="table table-striped table-bordered",
        formatters= {
        '% НП': '{:,.2%}'.format,
        '%': '{:,.2%}'.format
    } 
    )

    context["nonatt_html"] = nonatt_html

    return render(request, "nonatt_report.html", context)


@login_required(login_url="/login/")
@permission_required("grades_nonattendance.view_lessonresults")
def grades_report(request, student_id, term):
    if int(term) < 1 or int(term) > 4:
        raise Http404("Четверть не найдена.")

    term_start_date = QuarterSchedule.quarter_schedule[int(term - 1)]["start_date"]
    term_end_date = QuarterSchedule.quarter_schedule[int(term - 1)]["end_date"] + datetime.timedelta(days=1)

    student = get_object_or_404(AppUser, pk=student_id)

    grades_dataframe = get_grades_dataframe(term_start_date, term_end_date, student)

    context = {
        "student": student,
        "term": term,
    }

    if len(grades_dataframe.index) == 0:
        context["dataframe_no_index_flag"] = True
        return render(request, "nonatt_report.html", context)

    grades_html = grades_dataframe.to_html(
        classes="table table-striped table-bordered", 
        formatters={
            'Средний балл': '{:,.2}'.format,
        }
    )

    context["grades_html"] = grades_html

    return render(request, "grades_report.html", context) 


@login_required(login_url="/login/")
@permission_required("scheduling.view_lessonschedule")
def get_lesson(request, lesson_id):
    lesson_record = LessonSchedule.objects.get(id=lesson_id)

    if lesson_record.homework == None:
        lesson_record.homework = ""

    if lesson_record.lesson_material_file == None:
        lesson_materials_filename = ""
    else:
        lesson_materials_filename = lesson_record.lesson_material_file.name

    lesson_record = {
        "lesson_discipline": lesson_record.discipline_teacher.discipline.discipline_name,
        "lesson_materials": lesson_materials_filename,
        "lesson_date": lesson_record.lesson_holding_datetime_start.strftime("%d.%m.%Y"),
        "homework": lesson_record.homework
    }

    return JsonResponse({"lesson_record": lesson_record})


@login_required(login_url="/login/")
@permission_required("scheduling.view_lessonschedule")
def download_lesson_materials(request, lesson_id):
    lesson_record = get_object_or_404(LessonSchedule, pk=lesson_id)

    material_file = lesson_record.lesson_material_file

    return FileResponse(material_file, as_attachment=True)


@login_required(login_url="/login/")
@permission_required("scheduling.can_give_homework")
def delete_lesson_materials(request, lesson_id):
    lesson_record = get_object_or_404(LessonSchedule, pk=lesson_id)
    
    lesson_materials_path = lesson_record.lesson_material_file.path

    lesson_record.lesson_material_file = None
    lesson_record.save()

    default_storage.delete(lesson_materials_path)
    return HttpResponse()


@login_required(login_url="/login/")
@permission_required("scheduling.can_give_homework")
def set_homework(request, lesson_id):
    lesson_record = LessonSchedule.objects.get(id=lesson_id)

    if request.method == "POST":
        if request.POST["homework"].strip():
            lesson_record.homework = request.POST["homework"]
        else:
            lesson_record.homework = None

        form = LessonMaterialUploadForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_file = request.FILES.get('materials_file')
            if uploaded_file != None:
                lesson_record.lesson_material_file.save(uploaded_file.name, uploaded_file, save=True)

        lesson_record.save()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
