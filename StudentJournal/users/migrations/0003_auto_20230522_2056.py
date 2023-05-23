# Generated by Django 2.2.28 on 2023-05-22 20:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20230522_1059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classcode',
            name='homeroom_teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='homeroom_teacher_to_class', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='disciplineteacher',
            name='discipline',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discipline_to_teacher', to='users.DisciplineName'),
        ),
        migrations.AlterField(
            model_name='disciplineteacher',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_to_discipline', to=settings.AUTH_USER_MODEL),
        ),
    ]
