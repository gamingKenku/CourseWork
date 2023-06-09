# Generated by Django 2.2.28 on 2023-05-28 20:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('scheduling', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonschedule',
            name='class_code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.ClassCode'),
        ),
        migrations.AddField(
            model_name='lessonschedule',
            name='discipline_teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.DisciplineTeacher'),
        ),
        migrations.AlterUniqueTogether(
            name='lessonschedule',
            unique_together={('lesson_holding_datetime_start', 'classroom'), ('lesson_holding_datetime_start', 'class_code'), ('lesson_holding_datetime_start', 'discipline_teacher')},
        ),
    ]
