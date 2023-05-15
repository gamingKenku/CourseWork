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
        instance.set_password(self.cleaned_data["password"])
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
