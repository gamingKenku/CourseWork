from django.test import TestCase
from .models import ClassCode, AppUser
import datetime

class class_tests(TestCase):
    def test_unique_validation(self):
        teacher = AppUser()
        teacher.username = "teacher"
        teacher.set_password("5789a9321")
        teacher.age = 0
        teacher.date_of_birth = datetime.datetime.today()
        teacher.email = "teacher@mail.ru"
        teacher.save()

        code1 = ClassCode()
        code1.class_code = "ddddd"
        code1.homeroom_teacher = teacher
        code1.save()
        code2 = ClassCode()
        code2.class_code = "ddddd"
        code2.homeroom_teacher = teacher
        code2.save()
        code3 = ClassCode()
        code3.class_code = "ddddd"
        code3.homeroom_teacher = teacher
        code3.save()

        print(ClassCode.objects.get(id=1).class_code)
        print(ClassCode.objects.get(id=2).class_code)
        print(ClassCode.objects.get(id=3).class_code)
