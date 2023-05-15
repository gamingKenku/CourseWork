from django import forms
from users.models import AppUser, DisciplineName, DisciplineTeacher, ClassCode
from .models import LessonSchedule
from django.db.models import Q
import datetime


class LessonSheduleForm(forms.Form):
    start_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M', attrs={"hidden": True}))
    end_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M', attrs={"hidden": True}))
    discipline = forms.ModelChoiceField(DisciplineName.objects.all().order_by("discipline_name"), required=False)
    teacher = forms.ModelChoiceField(AppUser.objects.all().order_by("last_name", "first_name", "patronym"), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['discipline'].widget.attrs['class'] = 'discipline-select w-100'
        self.fields['teacher'].widget.attrs['class'] = 'teacher-select w-100'

    def is_valid(self):
        valid = super().is_valid()
        lesson_time_valid = True
        lesson_teacher_valid = True
        field_empty_valid = True

        if self.cleaned_data.get("discipline") == None and self.cleaned_data.get("teacher") == None:
            return True
        
        if self.cleaned_data.get("discipline") != None and self.cleaned_data.get("teacher") == None:
            self.add_error("teacher", "Поле должно быть заполнено.")
            field_empty_valid = False

        if self.cleaned_data.get("discipline") == None and self.cleaned_data.get("teacher") != None:
            self.add_error("discipline", "Поле должно быть заполнено.")
            field_empty_valid = False

        if LessonSchedule.objects.filter(lesson_holding_datetime_start__time = self.cleaned_data.get("start_time"), discipline_teacher__teacher = self.cleaned_data.get("teacher")).exists():
            self.add_error("teacher", "Этот учитель уже проводит занятия в это время.")
            lesson_time_valid = False

        if not DisciplineTeacher.objects.filter(teacher=self.cleaned_data.get("teacher"), discipline=self.cleaned_data.get("discipline")).exists() and field_empty_valid:
            self.add_error("teacher", "Этот учитель не преподает указанный предмет.")
            lesson_teacher_valid = False
        
        return valid and lesson_time_valid and lesson_teacher_valid and field_empty_valid
    

class LessonBellScheduleForm(forms.Form):
    start_time = forms.TimeField()
    end_time = forms.TimeField()
    
    def is_valid(self) -> bool:
        valid = super().is_valid()
        length_valid = True

        dummy_date = datetime.date(1970, 1, 1)
        start_time = datetime.datetime.combine(dummy_date, self.cleaned_data["start_time"])
        end_time = datetime.datetime.combine(dummy_date, self.cleaned_data["end_time"])

        length = end_time - start_time
        if length.total_seconds() / 60 != 45:
            length_valid = False
            self.add_error(None, "Длина урока должна быть 45 минут.")

        return valid and length_valid
    

class QuartersScheduleForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()


class ClassPicker(forms.Form):
    class_code = forms.ModelChoiceField(ClassCode.objects.all(), label="")