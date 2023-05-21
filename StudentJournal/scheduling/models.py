from django.db import models
from users.models import DisciplineTeacher, ClassCode

class LessonSchedule(models.Model):
    discipline_teacher = models.ForeignKey(DisciplineTeacher, on_delete=models.CASCADE)
    lesson_holding_datetime_start = models.DateTimeField()
    lesson_holding_datetime_end = models.DateTimeField()
    class_code = models.ForeignKey(ClassCode, on_delete=models.CASCADE)
    homework = models.CharField(max_length=255, blank=True, null=True)
    lesson_material_file = models.FileField(upload_to="materials", null=True, blank=True)
    sequence_num = models.SmallIntegerField()

    class Meta:
        unique_together = (('lesson_holding_datetime_start', 'class_code'),
                           ('lesson_holding_datetime_start', 'discipline_teacher'),
                           ('lesson_holding_datetime_start', 'sequence_num'),)
        permissions = (
            ('can_view_student_journal', 'Can view student journal'),
            ('can_view_class_journal', 'Can view class journal'),
            ('can_give_homework', 'Can give homework to class'),
        )
