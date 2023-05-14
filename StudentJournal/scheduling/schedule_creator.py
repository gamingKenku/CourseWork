import datetime
import os
import xml.etree.ElementTree as ET
import pytz
import locale

from django.db.models import Q

from users.models import ClassCode, DisciplineTeacher

from StudentJournal.settings import BASE_DIR

from .models import LessonSchedule


class QuarterSchedule:
    @staticmethod
    def __read_from_file():
        file_path = os.path.join(BASE_DIR, "scheduling\quarter_schedule.xml")

        quarter_schedule = []
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child in root.iter("quarter"):
            quarter_dict = {}
            quarter_dict["start_date"] = datetime.date.fromisoformat(child[0].text)
            quarter_dict["end_date"] = datetime.date.fromisoformat(child[1].text)
            quarter_schedule.append(quarter_dict)

        quarter_schedule = tuple(quarter_schedule)

        return quarter_schedule

    @staticmethod
    def save_to_file(quarter_struct):
        file_path = os.path.join(BASE_DIR, "scheduling\quarter_schedule.xml")
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child, quarter in zip(root.iter("quarter"), quarter_struct):
            child[0].text = quarter["start_date"].isoformat()
            child[1].text = quarter["end_date"].isoformat()

        tree.write(file_path)

    @staticmethod
    def initialise_from_file():
        QuarterSchedule.quarter_schedule = QuarterSchedule.__read_from_file()


    @staticmethod
    def get_current_term():
        today_date = datetime.date.today()
        current_term = None

        for i in range(0, len(QuarterSchedule.quarter_schedule)):
            if QuarterSchedule.quarter_schedule[i]["start_date"] >= today_date and QuarterSchedule.quarter_schedule[i]["end_date"] <= today_date:
                current_term = i
                break
    
        return current_term

    quarter_schedule = __read_from_file.__func__()


class BellSchedule:
    @staticmethod
    def __read_from_file():
        file_path = os.path.join(BASE_DIR, "scheduling\\bell_schedule.xml")
        bell_schedule = []
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child in root.iter("lesson"):
            bell_dict = {}
            bell_dict["start_time"] = datetime.time.fromisoformat(child[0].text)
            bell_dict["end_time"] = datetime.time.fromisoformat(child[1].text)
            bell_schedule.append(bell_dict)

        bell_schedule = tuple(bell_schedule)

        return bell_schedule

    @staticmethod
    def save_to_file(bell_ring_struct):
        file_path = os.path.join(BASE_DIR, "scheduling\\bell_schedule.xml")
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child, lesson in zip(root.iter("lesson"), bell_ring_struct):
            child[0].text = lesson["start_time"].isoformat()
            child[1].text = lesson["end_time"].isoformat()

        tree.write(file_path)

    @staticmethod
    def initialise_from_file():
        BellSchedule.bell_schedule = BellSchedule.__read_from_file()

    bell_schedule = __read_from_file.__func__()


class Lesson:
    def __init__(self, start, end, discipline_teacher=None) -> None:
        self.start_time = start
        self.end_time = end
        self.discipline_teacher = discipline_teacher

    def get_db_record(self, lesson_date, class_code):
        if self.discipline_teacher != None:
            return LessonSchedule(
                lesson_holding_datetime_start=datetime.datetime.combine(lesson_date, self.start_time),
                lesson_holding_datetime_end=datetime.datetime.combine(lesson_date, self.end_time),
                class_code=class_code,
                discipline_teacher=self.discipline_teacher
            )


class WeekScheduleCreator:
    def __init__(self, class_code, week_formset_dict=None) -> None:
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        self.schedule = {weekday: None for weekday in weekdays}
        self.class_code = class_code
        
        for day in self.schedule.keys():
            self.schedule[day] = [Lesson(lesson["start_time"], lesson["end_time"]) for lesson in BellSchedule.bell_schedule]

        if week_formset_dict != None:
            for day in self.schedule.keys():
                formset = week_formset_dict[f"{day}_lesson_form"]
                for i in range(0, len(self.schedule[day])):
                    teacher_id = formset[i].cleaned_data["teacher"]
                    discipline_id = formset[i].cleaned_data["discipline"]
                    if DisciplineTeacher.objects.filter(teacher=teacher_id, discipline=discipline_id).exists():
                        discipline_teacher_record = DisciplineTeacher.objects.get(teacher=teacher_id, discipline=discipline_id)
                        if discipline_teacher_record != None:
                            self.schedule[day][i].discipline_teacher = discipline_teacher_record        


    def reset_db_records_future(self, term: int):
        start = QuarterSchedule.quarter_schedule[term]["start_date"]
        end = QuarterSchedule.quarter_schedule[term]["end_date"]
        today_date = datetime.date.today()
        current_date = None

        if today_date >= start:
            start = today_date
            current_date = today_date

        LessonSchedule.objects.filter(Q(lesson_holding_datetime_start__date__gte=start) & Q(lesson_holding_datetime_start__date__lte=end)).delete()
        return current_date
        

    def reset_db_records(seld, term: int):
        start = QuarterSchedule.quarter_schedule[term]["start_date"]
        end = QuarterSchedule.quarter_schedule[term]["end_date"]
        records_to_delete = LessonSchedule.objects.filter(Q(lesson_holding_datetime_start__date__gte=start) & Q(lesson_holding_datetime_start__date__lte=end))

        if records_to_delete.exists():
            records_to_delete.delete()
            return True
        else:
            return False


    def reset_and_generate_schedule_records(self, term: int):
        current_date = self.reset_db_records_future(term)

        if current_date == None:
            current_date = QuarterSchedule.quarter_schedule[term]["start_date"]
            
        term_end_date = QuarterSchedule.quarter_schedule[term]["end_date"]
        batch = []

        while current_date <= term_end_date:
            weekday = current_date.strftime("%A").lower()
            if weekday == "sunday":
                current_date += datetime.timedelta(days=1)
                continue
            for lesson in self.schedule[weekday]:
                if lesson.discipline_teacher != None:
                    batch.append(lesson.get_db_record(current_date, self.class_code))

            if current_date.day == 20:
                LessonSchedule.objects.bulk_create(batch)
                batch = []

            current_date += datetime.timedelta(days=1)
        
        LessonSchedule.objects.bulk_create(batch)


