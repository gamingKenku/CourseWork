from django import forms
from users.models import AppUser, DisciplineName, DisciplineTeacher
from .models import LessonSchedule
from django.db.models import Q


class LessonSheduleForm(forms.Form):
    start_time = forms.TimeField()
    end_time = forms.TimeField()

    discipline = forms.ModelChoiceField(DisciplineName.objects.all())

    teacher = forms.ModelChoiceField(AppUser.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'discipline' in self.data:
            discipline_id = int(self.data.get('discipline'))
            self.fields['teacher'].queryset = DisciplineTeacher.objects.filter(discipline_id=discipline_id)

    def is_valid(self):
        valid = super().is_valid()

        if LessonSchedule.objects.filter(lesson_holding_datetime_start__time = self.start_time, teacher = self.teacher).exists():
            self.add_error("Этот учитель уже проводит занятия в это время.")
            return False
        
        return valid
