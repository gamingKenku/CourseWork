import datetime
from django.shortcuts import get_object_or_404, render
from django.db.models import Q, QuerySet
from django.http import HttpResponseRedirect, Http404
from scheduling.models import LessonSchedule
from scheduling.schedule_creator import QuarterSchedule
from users.models import ClassCode, ClassStudent, DisciplineName, AppUser
from .models import Grade, NonAttendance

def class_journal(request, class_id, discipline_id, term):
    context = {}

    GRADES = (
        "1", "2", "3", "4", "5"
    )

    class_code = get_object_or_404(ClassCode, id=class_id)
    discipline = get_object_or_404(DisciplineName, id=discipline_id)
    students_records = ClassStudent.objects.filter(class_code=class_code)
    int_term = int(term) - 1
    existing_grades_nonattt = get_grades_nonatt_as_dict(students_records, int_term)

    if request.method == "POST":
        post_data = request.POST.copy()
        del post_data["csrfmiddlewaretoken"]

        if grades_nonatt_is_valid(post_data):
            filtered_grades_nonatt = {
                key: value for key, value in post_data.items() if key not in existing_grades_nonattt.keys()
            }
            print(filtered_grades_nonatt)

            for grade_nonatt in filtered_grades_nonatt.items():
                data = grade_nonatt[0].split("-")

                student = AppUser.objects.get(id=int(data[1]))
                lesson = LessonSchedule.objects.get(id=int(data[2]))

                if grade_nonatt[1] in GRADES:
                    grade = int(grade_nonatt[1])
                    Grade.objects.create(student=student, lesson=lesson, grade=grade)
                else:
                    non_attendance_reason = grade_nonatt[1]
                    NonAttendance.objects.create(student=student, lesson=lesson, non_attendance_reason=non_attendance_reason)

            return HttpResponseRedirect("/")
        else:
            context.update(post_data)
            print("grades and nonatt non valid")
    else:
        context.update(existing_grades_nonattt)

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


def get_grades_nonatt_as_dict(students_records, term: int) -> dict:
    res = {}

    term_start_date = QuarterSchedule.quarter_schedule[term]["start_date"]
    term_end_date = QuarterSchedule.quarter_schedule[term]["end_date"] + datetime.timedelta(days=1)
    students_ids = students_records.values("student")

    grades = Grade.objects.filter(
        Q(lesson__lesson_holding_datetime_start__gte=term_start_date) & 
        Q(lesson__lesson_holding_datetime_start__lte=term_end_date) & 
        Q(student_id__in = students_ids)
    )

    res.update(
        {
            f"grade_nonatt-{grade.student.id}-{grade.lesson.id}": grade.grade for grade in grades
        }
    )

    non_attendances = NonAttendance.objects.filter(
        Q(lesson__lesson_holding_datetime_start__gte=term_start_date) & 
        Q(lesson__lesson_holding_datetime_start__lte=term_end_date) & 
        Q(student_id__in = students_ids)
    )

    res.update(
        {
            f"grade_nonatt-{non_attendance.student.id}-{non_attendance.lesson.id}": non_attendance.non_attendance_reason for non_attendance in non_attendances
        }
    )

    return res


def grades_nonatt_is_valid(post_data) -> bool:
    NON_ATTENDANCE_REASONS = (
        "УП", "Н"
    )
    GRADES = (
        "1", "2", "3", "4", "5"
    )

    for item in post_data.items():
        if item[1] not in GRADES and item[1] not in NON_ATTENDANCE_REASONS:
            return False
        
    return True


