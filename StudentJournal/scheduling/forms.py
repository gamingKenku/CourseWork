from django import forms
from users.models import AppUser, DisciplineName, DisciplineTeacher, ClassCode, ClassDisciplines
from .models import LessonSchedule
from django.db.models import Q
import datetime


class LessonSheduleForm(forms.Form):
    start_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M', attrs={"hidden": True}))
    end_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M', attrs={"hidden": True}))
    class_code = forms.ModelChoiceField(ClassCode.objects.all(), required=True, widget=forms.HiddenInput())
    discipline = forms.ModelChoiceField(DisciplineName.objects.all(), required=False)
    teacher = forms.ModelChoiceField(AppUser.objects.all().order_by("last_name", "first_name", "patronym"), required=False)
    term_num = forms.IntegerField(required=True, widget=forms.HiddenInput())
    classroom = forms.CharField(max_length=5, required=False, widget=forms.TextInput(attrs={"style":"width: 100%;"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['discipline'].widget.attrs['class'] = 'discipline-select w-100'
        self.fields['teacher'].widget.attrs['class'] = 'teacher-select w-100'


    def is_valid(self):
        valid = super().is_valid()

        lesson_time_valid = True
        lesson_teacher_valid = True
        classroom_valid = True

        discipline = self.cleaned_data.get("discipline")
        teacher = self.cleaned_data.get("teacher")
        class_code = self.cleaned_data.get("class_code")
        classroom = self.cleaned_data.get("classroom")

        if not (discipline or teacher or classroom):
            return True
        
        if not teacher:
            self.add_error("teacher", "Поле должно быть заполнено.")
            return False

        if not discipline:
            self.add_error("discipline", "Поле должно быть заполнено.")
            return False
        
        if not classroom:
            self.add_error("classroom", "Поле должно быть заполнено.")
            return False

        if LessonSchedule.objects.filter(
                lesson_holding_datetime_start__hour = self.cleaned_data.get("start_time").hour, 
                lesson_holding_datetime_start__minute = self.cleaned_data.get("start_time").minute, 
                discipline_teacher__teacher = teacher,
                term_num = self.cleaned_data.get("term_num")
            ).exclude(class_code=class_code).exclude(lesson_holding_datetime_start__lte = datetime.datetime.now()).exists():
            self.add_error("teacher", "Этот учитель уже проводит занятия в это время.")
            lesson_time_valid = False

        if LessonSchedule.objects.filter(
                lesson_holding_datetime_start__hour = self.cleaned_data.get("start_time").hour, 
                lesson_holding_datetime_start__minute = self.cleaned_data.get("start_time").minute, 
                classroom = classroom,
                term_num = self.cleaned_data.get("term_num")
            ).exclude(class_code=class_code).exclude(lesson_holding_datetime_start__lte = datetime.datetime.now()).exists():
            self.add_error("classroom", "В этом классе уже проводятся занятия в это время.")
            classroom_valid = False

        if not DisciplineTeacher.objects.filter(teacher=teacher, discipline=discipline).exists():
            self.add_error("teacher", "Этот учитель не преподает указанный предмет.")
            lesson_teacher_valid = False
        
        return valid and lesson_time_valid and lesson_teacher_valid and classroom_valid
    

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
    class_code = forms.ModelChoiceField(ClassCode.objects.none(), label="")

    def __init__(self, teacher=None, *args, **kwargs):
        super(ClassPicker, self).__init__(*args, **kwargs)

        if teacher:
            if teacher.has_perm("scheduling.add_lessonschedule"):
                self.fields['class_code'].queryset = ClassCode.objects.all()
                return

            teached_lessons = LessonSchedule.objects.filter(discipline_teacher__teacher = teacher)
            class_code_ids = teached_lessons.values("class_code_id")
            teached_classes = ClassCode.objects.filter(id__in = class_code_ids)
            homeroomed_classes = ClassCode.objects.filter(homeroom_teacher=teacher)

            queryset = teached_classes.union(homeroomed_classes)

            self.fields['class_code'].queryset = queryset


class DisciplineNamePicker(forms.Form):
    discipline_name = forms.ModelChoiceField(DisciplineName.objects.none(), label="")

    def __init__(self, teacher=None, *args, **kwargs):
        super(DisciplineNamePicker, self).__init__(*args, **kwargs)

        if teacher:
            if teacher.has_perm("scheduling.add_lessonschedule"):
                self.fields['discipline_name'].queryset = DisciplineName.objects.all()
                return
            
            attached_disciplines = DisciplineTeacher.objects.filter(teacher=teacher)
            discipline_ids = attached_disciplines.values("discipline_id")
            disciplines = DisciplineName.objects.filter(id__in=discipline_ids)

            self.fields['discipline_name'].queryset = disciplines


class TermPicker(forms.Form):
    FIRST = "1"
    SECOND = "2"
    THIRD = "3"
    FOURTH = "4"

    CHOICES = [
        (FIRST, "Первый"),
        (SECOND, "Второй"),
        (THIRD, "Третий"),
        (FOURTH, "Четвертый"),
    ]

    term = forms.ChoiceField(choices=CHOICES, label="")


class LessonMaterialUploadForm(forms.Form):
    materials_file = forms.FileField(label="Материалы к уроку", required=False, widget=forms.FileInput(attrs={"id": "id-materials-file"}))