from django import forms
from users.models import AppUser, DisciplineName, DisciplineTeacher
from django.db.models import Q


class LessonDisciplineTeacherForm(forms.Form):
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