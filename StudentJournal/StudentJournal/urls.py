"""
URL configuration for StudentJournal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import scheduling.views
import users.views
import grades_nonattendance.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', users.views.login_user),
    path('logout/', users.views.logout_user),
    path('teachers/', users.views.teachers_view),
    path('teachers/add_discipline/', users.views.add_discipline),
    path('teachers/add_discipline_to_teacher/', users.views.add_discipline_to_teacher),
    path('teachers/detach_discipline/<int:discipline_record_id>', users.views.detach_discipline),
    path('students/', users.views.students_view),
    path('users/<int:user_id>', users.views.user_info),
    path('users/<int:user_id>/edit', users.views.user_edit),
    path('students/add_class/', users.views.add_class),
    path('account/', users.views.account),
    path('classes/', users.views.classes),
    path('classes/<int:class_id>', users.views.class_info),
    path('classes/<int:class_id>/advance', users.views.class_advance),
    path('classes/all_classes_advance/', users.views.all_classes_advance),
    path('schedule/create/<int:class_id>', scheduling.views.create_schedule),
    path('schedule/edit/<int:class_id>', scheduling.views.edit_schedule),
    path('schedule/reset/<int:class_id>', scheduling.views.reset_schedule),
    path('schedule/edit_bell_quarter/', scheduling.views.bell_quarter_edit),
    path('schedule/', scheduling.views.schedule_menu),
    path('discipline_teacher/<int:discipline_id>/', scheduling.views.get_teachers_for_discipline),
    path('schedule/student_journal/<str:week_start_date>/<str:week_end_date>/', scheduling.views.student_journal),
    path('schedule/class_journal/<str:class_id>/<str:discipline_id>/<str:term>/', scheduling.views.class_journal),
    path('', users.views.index)
]
