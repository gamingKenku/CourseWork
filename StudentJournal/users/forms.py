from django import forms
from django.forms import ModelForm
from .models import AppUser, DisciplineName, ClassCode
from bootstrap_datepicker_plus.widgets import DatePickerInput
from users.methods.defs import num_years

class LoginForm(forms.Form):
    username = forms.CharField(label="Имя пользователя:")
    password = forms.CharField(label="Пароль:", widget=forms.PasswordInput)


class UserForm(ModelForm):
    def save(self, commit=True):
        instance = super(UserForm, self).save(commit=False)
        instance.age = num_years(self.cleaned_data["date_of_birth"])

        if commit:
            instance.save()
        return instance

    class Meta:
        model = AppUser
        fields = ["username", "password", "first_name", "last_name", "patronym", "email", "date_of_birth"]
        labels = {
            "username": "Имя пользователя:",
            "password": "Пароль:",
            "first_name": "Имя:",
            "last_name": "Фамилия:",
            "patronym": "Отчество:",
            "email": "Электронная почта:",
            "date_of_birth": "Дата рождения:"
        }
        widgets = {
            "username": forms.TextInput(attrs={'placeholder': 'Введите имя пользователя...', 'class':'mb-1'}),
            "password": forms.PasswordInput(attrs={'placeholder': 'Введите пароль...', 'class':'mb-1'}),
            "first_name": forms.TextInput(attrs={'placeholder': 'Введите имя...', 'class':'mb-1'}),
            "last_name": forms.TextInput(attrs={'placeholder': 'Введите фамилию...', 'class':'mb-1'}),
            "patronym": forms.TextInput(attrs={'placeholder': 'Введите отчество...', 'class':'mb-1'}),
            "email": forms.TextInput(attrs={'placeholder': 'Введите адрес электронной почты...', 'class':'mb-1'}),
            "date_of_birth": DatePickerInput(attrs={'placeholder': 'Укажите дату рождения...', 'class':'mb-1'})
        }


# class StudentParentForm(forms.Form):
#     student_form = UserForm(prefix="student_form")
#     mother_form = UserForm(prefix="mother_form")
#     father_form = UserForm(prefix="father_form")

#     def is_valid(self):
#         parent_form_valid = super().is_valid()

#         student_form_valid = self.student_form.is_valid()
#         mother_form_valid = self.mother_form.is_valid()
#         father_form_valid = self.father_form.is_valid()

#         student_username = self.cleaned_data.get('student_form-username')
#         mother_username = self.cleaned_data.get('mother_form-username')
#         father_username = self.cleaned_data.get('father_form-username')

#         student_email = self.cleaned_data.get('student_form-email')
#         mother_email = self.cleaned_data.get('mother_form-email')
#         father_email = self.cleaned_data.get('father_form-email')

#         if len(set([student_username, mother_username, father_username])) < 3 or \
#             len(set([student_email, mother_email, father_email])) < 3:
#             self.add_error(None, "Имена пользователей должны быть разными.")
#             return False

#         if not parent_form_valid or not student_form_valid or not mother_form_valid or not father_form_valid:
#             return False

#         return True


class DisciplineNameForm(ModelForm):
    class Meta:
        model = DisciplineName
        fields = ["discipline_name"]
        labels = {
            'discipline_name': 'Название предмета:'
        }
        widgets = {
            'discipline_name': forms.TextInput(attrs={'placeholder': 'Введите название предмета...', 'class':'mb-1'})
        }


class ClassCodeForm(ModelForm):
    class Meta:
        model = ClassCode
        fields = ["class_code"]
        labels = {
            'class_code': 'Код класса:'
        }
        widgets = {
            'class_code': forms.TextInput(attrs={'placeholder': 'Введите код класса...', 'class':'mb-1'})
        }
