from django.db import models
from users.models import DisciplineTeacher, ClassCode

class LessonSchedule(models.Model):
    discipline_teacher = models.ForeignKey(DisciplineTeacher, on_delete=models.CASCADE)
    lesson_holding_datetime = models.DateTimeField()
    student_class = models.ForeignKey(ClassCode, on_delete=models.CASCADE)
    homework = models.CharField(max_length=255, blank=True, null=True)
    lesson_material_text = models.CharField(max_length=255, blank=True, null=True)
    lesson_material_file_path = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = (('lesson_holding_datetime', 'student_class'),
                           ('lesson_holding_datetime', 'discipline_teacher'))
        permissions = (
            ('can_view_student_journal', 'Can view student journal'),
            ('can_view_class_journal', 'Can view class journal'),
            ('can_give_homework', 'Can give homework to class'),
        )
