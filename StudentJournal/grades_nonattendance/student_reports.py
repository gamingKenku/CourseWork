import datetime
import pandas as pd
from django.db.models import Q
from scheduling.models import LessonSchedule
from scheduling.schedule_creator import QuarterSchedule
from .models import LessonResults;
from scheduling.schedule_creator import QuarterSchedule


def get_grades_nonatt_as_dict(students_records, term: int) -> dict:
    res = {}

    term_start_date = QuarterSchedule.quarter_schedule[term]["start_date"]
    term_end_date = QuarterSchedule.quarter_schedule[term]["end_date"] + datetime.timedelta(days=1)
    students_ids = students_records.values("student")

    results = LessonResults.objects.filter(
        Q(lesson__lesson_holding_datetime_start__gte=term_start_date) & 
        Q(lesson__lesson_holding_datetime_start__lte=term_end_date) & 
        Q(student_id__in = students_ids)
    )

    res.update(
        {
            f"grade-nonatt-{result.student.id}-{result.lesson.id}": result.grade for result in results if result.grade is not None
        }
    )
    res.update(
        {
            f"grade-nonatt-{result.student.id}-{result.lesson.id}": result.non_attendance_reason for result in results if result.non_attendance_reason is not None and result.non_attendance_reason != ""
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
        if item[1] not in GRADES and item[1] not in NON_ATTENDANCE_REASONS and item[1] != "DE":
            return False
        
    return True


def get_week_numbers(start_date, end_date):
    week_numbers = []
    current_date = start_date

    while current_date <= end_date:
        week_number = current_date.isocalendar()[1]  # Get the ISO week number
        week_numbers.append(week_number)
        current_date += datetime.timedelta(days=7)  # Move to the next week

    return week_numbers


def get_nonatt_dataframe(term_start_date, term_end_date, student):
    nonatt_records = LessonResults.objects.filter(
        Q(student = student) & 
        Q(lesson__lesson_holding_datetime_start__gte = term_start_date) & 
        Q(lesson__lesson_holding_datetime_start__lte = term_end_date) &
        Q(non_attendance_reason__isnull = False)
    ).exclude(non_attendance_reason = "")

    indexes_list = list(set(LessonSchedule.objects.filter(
        Q(lesson_holding_datetime_start__gte = term_start_date) & 
        Q(lesson_holding_datetime_start__lte = term_end_date)
    ).values_list("discipline_teacher__discipline__discipline_name", flat=True)))
    columns_list = get_week_numbers(term_start_date, term_end_date)
    week_number_offset = columns_list[0] - 1
    columns_list = [week_number - week_number_offset for week_number in columns_list]
    nonatt_dataframe = pd.DataFrame(0, index=indexes_list, columns=columns_list)

    for nonatt_record in nonatt_records:
        week_number = nonatt_record.lesson.lesson_holding_datetime_start.isocalendar()[1] - week_number_offset
        discipline = nonatt_record.lesson.discipline_teacher.discipline.discipline_name

        nonatt_dataframe.at[discipline, week_number] += 1

    valid_nonattendance = []
    invalid_nonattendance = []
    overall_nonattendance = nonatt_dataframe.sum(axis=1)
    overall_nonattendance_percent = []
    invalid_nonattendance_percent = []
    overall_lessons_list = []

    for nonatt_index in nonatt_dataframe.index:
        overall_lessons = LessonSchedule.objects.filter(
            Q(lesson_holding_datetime_start__gte = term_start_date) & 
            Q(lesson_holding_datetime_start__lte = term_end_date) &
            Q(discipline_teacher__discipline__discipline_name = nonatt_index) &
            Q(class_code = student.student_to_class.get().class_code)
        ).count()

        overall_lessons_list.append(overall_lessons)
        valid_nonattendance.append(nonatt_records.filter(Q(non_attendance_reason = "УП") & Q(lesson__discipline_teacher__discipline__discipline_name=nonatt_index)).count())
        invalid_nonattendance.append(nonatt_records.filter(Q(non_attendance_reason = "Н") & Q(lesson__discipline_teacher__discipline__discipline_name=nonatt_index)).count())

        overall_nonattendance_percent.append(
            (valid_nonattendance[-1] + invalid_nonattendance[-1]) / overall_lessons
        )

        invalid_nonattendance_percent.append(
            invalid_nonattendance[-1] / overall_lessons
        )

    nonatt_dataframe["НП"] = invalid_nonattendance
    nonatt_dataframe["УП"] = valid_nonattendance
    nonatt_dataframe["Общая сумма"] = overall_nonattendance
    nonatt_dataframe["% НП"] = invalid_nonattendance_percent
    nonatt_dataframe["%"] = overall_nonattendance_percent 
    nonatt_dataframe["Всего уроков"] = overall_lessons_list
    nonatt_dataframe[columns_list] = nonatt_dataframe[columns_list].astype(int)
    nonatt_dataframe.loc["Всего"] = pd.Series(
        [
            nonatt_dataframe["НП"].sum(), 
            nonatt_dataframe["УП"].sum(), 
            nonatt_dataframe["Общая сумма"].sum(),
            nonatt_dataframe["НП"].sum() / nonatt_dataframe["Всего уроков"].sum(),
            nonatt_dataframe["Общая сумма"].sum() / nonatt_dataframe["Всего уроков"].sum(),
            nonatt_dataframe["Всего уроков"].sum()
        ],
        index=["НП", "УП", "Общая сумма", "% НП", "%", "Всего уроков"]
    )
    nonatt_dataframe.fillna("", inplace=True)

    nonatt_dataframe.iloc[:-1, :-5] = nonatt_dataframe.iloc[:-1, :-5].astype(int)
    nonatt_dataframe["НП"] = nonatt_dataframe["НП"].astype(int)
    nonatt_dataframe["УП"] = nonatt_dataframe["УП"].astype(int)
    nonatt_dataframe["Общая сумма"] = nonatt_dataframe["Общая сумма"].astype(int)
    nonatt_dataframe["Всего уроков"] = nonatt_dataframe["Всего уроков"].astype(int)
    return nonatt_dataframe


def get_grades_dataframe(term_start_date, term_end_date, student):
    grade_records = LessonResults.objects.filter(
        Q(student = student) & 
        Q(lesson__lesson_holding_datetime_start__gte = term_start_date) & 
        Q(lesson__lesson_holding_datetime_start__lte = term_end_date) &
        Q(grade__isnull = False)
    )

    indexes_list = list(set(LessonSchedule.objects.filter(
        Q(lesson_holding_datetime_start__gte = term_start_date) & 
        Q(lesson_holding_datetime_start__lte = term_end_date)
    ).values_list("discipline_teacher__discipline__discipline_name", flat=True)))
    
    columns_list = [1, 2, 3, 4, 5]
    grades_dataframe = pd.DataFrame(0, index=indexes_list, columns=columns_list)

    for grade_record in grade_records:
        grade = grade_record.grade
        discipline = grade_record.lesson.discipline_teacher.discipline.discipline_name

        grades_dataframe.at[discipline, grade] += 1

    grades_dataframe["Средний балл"] = grades_dataframe.apply(lambda row: row.dot(row.index.astype(int)), axis=1) / grades_dataframe.sum(axis=1)
    return grades_dataframe   