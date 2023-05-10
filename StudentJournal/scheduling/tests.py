from django.test import TestCase, Client
from django.http import QueryDict


class ScheduleCreatorTests(TestCase):
    def setUp(self):
        self.c = Client()

    def test_schedule_create_context(self):
        print("test 1 start")

        response = self.c.get("/schedule/create_schedule/")

        print("Response code:", response.status_code)
        print("--------------------------------")
        print("Responce context:")
        print(response.context)
        print("Responce content:")
        print(response.content)
