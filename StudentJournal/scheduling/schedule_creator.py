import datetime
import os
import xml.etree.ElementTree as ET

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
            quarter_dict["start"] = datetime.date.fromisoformat(child[0].text)
            quarter_dict["end"] = datetime.date.fromisoformat(child[1].text)
            quarter_schedule.append(quarter_dict)

        quarter_schedule = tuple(quarter_schedule)

        return quarter_schedule

    @staticmethod
    def save_to_file(quarter_struct):
        file_path = os.path.join(BASE_DIR, "scheduling\quarter_schedule.xml")
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child, quarter in zip(root.iter("quarter"), quarter_struct):
            child[0].text = quarter["start"].isoformat()
            child[1].text = quarter["end"].isoformat()

        tree.write(file_path)

    @staticmethod
    def initialise_from_file():
        QuarterSchedule.quarter_schedule = QuarterSchedule.__read_from_file()

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


class WeekSchedule:
    def __init__(self, class_code=None, post_data=None) -> None:
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        self.schedule = {weekday: None for weekday in weekdays}
        
        for day in self.schedule.keys():
            self.schedule[day] = [Lesson(lesson["start_time"], lesson["end_time"]) for lesson in BellSchedule.bell_schedule]

        if class_code != None:
            self.class_code = class_code

        if post_data != None:
            pass
        
    def generate_schedule_records(self, term):
        current_date = datetime.date.fromisoformat(QuarterSchedule.quarter_schedule[term]["start"])
        term_end_date = datetime.date.fromisoformat(QuarterSchedule.quarter_schedule[term]["end"])
        batch = []

        while current_date <= term_end_date:
            weekday = current_date.strftime("%A").lower()
            for lesson in self.schedule[weekday]:
                if lesson.discipline_teacher != None:
                    batch.append(lesson.get_db_record(current_date, self.class_code))

            if current_date.day == 20:
                LessonSchedule.objects.bulk_create(batch)
                batch = []

            current_date += datetime.timedelta(1)

