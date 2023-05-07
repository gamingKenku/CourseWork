from django.http import QueryDict
from django.test import Client, TestCase
from .models import ClassCode, AppUser
import datetime
from django.contrib.auth.models import Group

class class_tests(TestCase):
    # def test_unique_validation(self):
    #     teacher = AppUser()
    #     teacher.username = "teacher"
    #     teacher.set_password("5789a9321")
    #     teacher.age = 0
    #     teacher.date_of_birth = datetime.datetime.today()
    #     teacher.email = "teacher@mail.ru"
    #     teacher.save()

    #     code1 = ClassCode()
    #     code1.class_code = "ddddd"
    #     code1.homeroom_teacher = teacher
    #     code1.save()
    #     code2 = ClassCode()
    #     code2.class_code = "ddddd"
    #     code2.homeroom_teacher = teacher
    #     code2.save()
    #     code3 = ClassCode()
    #     code3.class_code = "ddddd"
    #     code3.homeroom_teacher = teacher
    #     code3.save()

    #     print(ClassCode.objects.get(id=1).class_code)
    #     print(ClassCode.objects.get(id=2).class_code)
    #     print(ClassCode.objects.get(id=3).class_code)
    
    def test_add_student(self):
        c = Client()

        teacher = AppUser()
        teacher.username = "uchitel"
        teacher.set_password("5789a9321")
        teacher.email = "teacher@mail.ru"
        teacher.save()

        Group.objects.create(name='student')
        Group.objects.create(name='parent')
        ClassCode.objects.create(class_code="1А", homeroom_teacher=teacher)
        
        student_form_data = {
            'username': 'uchitel', 
            'password': '5789a9321',
            'first_name': 'imya',
            'last_name': 'familya',
            'patronym': 'otchestvo',
            'email': 'person1@mail.ru',
            'date_of_birth': '2023-05-03'
            }
        mother_form_data = {
            'username': 'uchitel', 
            'password': '5789a9321',
            'first_name': 'imya',
            'last_name': 'familya',
            'patronym': 'otchestvo',
            'email': 'person2@mail.ru',
            'date_of_birth': '2023-05-03'
            }
        father_form_data = {
            'username': 'uchitel', 
            'password': '5789a9321',
            'first_name': 'imya',
            'last_name': 'familya',
            'patronym': 'otchestvo',
            'email': 'person3@mail.ru',
            'date_of_birth': '2023-05-03'
            }

        # combine form data into a dictionary with prefixes as keys
        data = {'student_form': student_form_data, 'mother_form': mother_form_data, "father_form": father_form_data}

        # create a QueryDict from the data dictionary
        query_dict = QueryDict('', mutable=True)
        for prefix, form_data in data.items():
            for field, value in form_data.items():
                query_dict.update({f"{prefix}-{field}": value})
        query_dict.update({"class_select": 1})

        print(query_dict)

        response = c.post('/students/', data=query_dict)
        print(response.status_code)

        print(AppUser.objects.all())
