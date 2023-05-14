# Generated by Django 2.2.28 on 2023-05-13 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LessonSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lesson_holding_datetime_start', models.DateTimeField()),
                ('lesson_holding_datetime_end', models.DateTimeField()),
                ('homework', models.CharField(blank=True, max_length=255, null=True)),
                ('lesson_material_text', models.CharField(blank=True, max_length=255, null=True)),
                ('lesson_material_file_path', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'permissions': (('can_view_student_journal', 'Can view student journal'), ('can_view_class_journal', 'Can view class journal'), ('can_give_homework', 'Can give homework to class')),
            },
        ),
    ]
