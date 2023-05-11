from django import forms
from users.models import AppUser, DisciplineName, DisciplineTeacher
from .models import LessonSchedule
from django.db.models import Q


class LessonSheduleForm(forms.Form):
    start_time = forms.TimeField()
    end_time = forms.TimeField()

    discipline = forms.ModelChoiceField(DisciplineName.objects.all().order_by("discipline_name"))

    teacher = forms.ModelChoiceField(AppUser.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'discipline' in self.data:
            discipline_id = int(self.data.get('discipline'))
            self.fields['teacher'].queryset = DisciplineTeacher.objects.filter(discipline_id=discipline_id).order_by("first_name", "last_name", "patronym")

    def is_valid(self):
        valid = super().is_valid()
        lesson_time_valid = True
        lesson_teacher_valid = True

        if LessonSchedule.objects.filter(lesson_holding_datetime_start__time = self.data.get("start_time"), discipline_teacher__teacher = self.data.get("teacher")).exists():
            self.add_error("teacher", "Этот учитель уже проводит занятия в это время.")
            lesson_time_valid = False

        if not DisciplineTeacher.objects.filter(teacher=self.data.get("teacher"), discipline=self.data.get("discipline")).exists():
            self.add_error("teacher", "Этот учитель не преподает указанный предмет.")
            lesson_teacher_valid = False
        
        return valid and lesson_time_valid and lesson_teacher_valid
