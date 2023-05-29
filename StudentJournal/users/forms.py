from django import forms
from django.forms import ModelForm
from .models import AppUser, DisciplineName, ClassCode, ClassDisciplines
from bootstrap_datepicker_plus.widgets import DatePickerInput
from users.methods.defs import num_years

class LoginForm(forms.Form):
    error_css_class = 'text_danger'
    username = forms.CharField(label="", widget=forms.TextInput(attrs={"placeholder": "Имя пользователя", "class": "form-control mb-3 mt-3"}))
    password = forms.CharField(label="", widget=forms.PasswordInput(attrs={"placeholder": "Пароль",  "class": "form-control mb-3 mt-3"}))


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

    def is_valid(self) -> bool:
        valid = super().is_valid()
        format_valid = True
        unique_valid = True

        cyrillic_symbols = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'.upper()

        class_code = self.cleaned_data.get("class_code")
        paral = class_code[-1]
        class_num = class_code[:-1]

        if paral not in cyrillic_symbols or not class_num.isnumeric() or int(class_num) < 1 or int(class_num) > 11:
            self.add_error("class_code", "Класс введен в неверном формате")
            format_valid = False

        if ClassCode.objects.filter(class_code=class_code).exists():
            self.add_error("class_code", "Такой класс уже существует")
            unique_valid = False

        return valid and format_valid and unique_valid

class ClassDisciplinesForm(ModelForm):
    class Meta:
        model = ClassDisciplines
        fields = ["class_num", "studied_disciplines"]
        labels = {
            "class_num": "Целая часть номера класса:",
            "studied_disciplines": "Изучаемые дисциплины"
        }

    class_num = forms.IntegerField(widget=forms.HiddenInput)
    studied_disciplines = forms.ModelMultipleChoiceField(
        queryset=DisciplineName.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )