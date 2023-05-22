from django.test import TestCase
from users.models import AppUser
from .views import nonatt_report

class NonattReportTests(TestCase):
    def setUp(self) -> None:
        return super().setUp()
    

    def test_nonatt_report(self):
        print("test 1 start")
        
        student = AppUser.objects.get(pk=3)
        request = self.client.get('/')

        nonatt_report(request, 3, 4)