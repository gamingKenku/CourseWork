from django import forms
from users.models import AppUser, DisciplineName, DisciplineTeacher
from .models import LessonSchedule
from django.db.models import Q


class LessonSheduleForm(forms.Form):
    start_time = forms.TimeField(widget=forms.HiddenInput)

    teacher = forms.ModelChoiceField(
        AppUser.objects.filter(
            Q(groups__name="teacher")
            | Q(groups__name="director")
            | Q(groups__name="head_teacher")
        )
    )
    discipline = forms.ModelChoiceField(DisciplineName.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'discipline' in self.data:
            teacher_id = int(self.data.get('teacher'))
            self.fields['discipline'].queryset = DisciplineTeacher.objects.filter(teacher_id=teacher_id)

    def is_valid(self):
        valid = super().is_valid

        if LessonSchedule.objects.filter(lesson_holding_datetime_start__time = self.start_time, teacher = self.teacher).exists():
            self.add_error("Этот учитель уже проводит занятия в это время.")
            return False
        
        return valid
