from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from scheduling.models import LessonSchedule
from users.models import AppUser


class LessonResults(models.Model):
    student = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    lesson = models.ForeignKey(LessonSchedule, on_delete=models.CASCADE, related_name="lesson_to_results")
    remark = models.CharField(max_length=127, null=True, blank=True)
    non_attendance_reason = models.CharField(max_length=5, null=True, blank=True)
    grade = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)