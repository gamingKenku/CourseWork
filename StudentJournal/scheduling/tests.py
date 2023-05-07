from django.test import TestCase, Client
from .models import ClassStudent
from django.http import QueryDict

class StudentFormText(TestCase):    
    def test_add_student(self):
        c = Client()
        
        # assume two forms with prefixes 'form1' and 'form2'
        student_form_data = {
            'username': 'uchenik', 
            'password': '5789a9321',
            'first_name': 'imya',
            'last_name': 'familya',
            'patronym': 'otchestvo',
            'email': 'person1@mail.ru',
            'date_of_birth': '2023-05-03'
            }
        mother_form_data = {
            'username': 'mat', 
            'password': '5789a9321',
            'first_name': 'imya',
            'last_name': 'familya',
            'patronym': 'otchestvo',
            'email': 'person2@mail.ru',
            'date_of_birth': '2023-05-03'
            }
        father_form_data = {
            'username': 'otec', 
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
        print(dict(query_dict))

        response = c.post('/students/', data=query_dict)
        print(response.status_code)