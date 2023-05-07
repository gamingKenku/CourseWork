from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from users.forms import LoginForm, UserForm, DisciplineNameForm, ClassCodeForm
from users.models import AppUser, DisciplineName, DisciplineTeacher, ClassCode, ClassStudent, Parents
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from scheduling.methods.defs import num_years
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
import datetime
from django.core.exceptions import ValidationError


roles_to_russian_dict = {
    "student": "ученик",
    "teacher": "учитель",
    "head_teacher": "завуч",
    "director": "директор",
    "parent": "родитель"
}


@login_required(login_url="login/")
def index(request):
    return render(request, "index.html")


def login_user(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect("/")
    
    form = LoginForm()
    return render(request, 'login.html', context={"form": form})


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect("/login/")


def account(request):
    return render(request, "account.html", context={})


def teachers_view(request):
    teachers = AppUser.objects.filter(Q(groups__name="teacher") | Q(groups__name="director") | Q(groups__name="head_teacher"))
    disciplines = DisciplineName.objects.all()
    discipline_teachers = DisciplineTeacher.objects.all()
    classes = ClassCode.objects.all()

    disciplines_dict = {}
    for teacher in teachers:
        records = discipline_teachers.filter(teacher__id = teacher.id)
        for record in records:
            if record.teacher not in disciplines_dict.keys():
                disciplines_dict[record.teacher] = [record.discipline.discipline_name]
            else:
                disciplines_dict[record.teacher].append(record.discipline.discipline_name)

    if request.method == "POST":
        teacher_form = UserForm(request.POST)
        if teacher_form.is_valid():
            teacher = AppUser()
            teacher.username = teacher_form.cleaned_data["username"]
            teacher.set_password(teacher_form.cleaned_data["password"])
            teacher.email = teacher_form.cleaned_data["email"]
            teacher.first_name = teacher_form.cleaned_data["first_name"]
            teacher.last_name = teacher_form.cleaned_data["last_name"]
            teacher.patronym = teacher_form.cleaned_data["patronym"]
            teacher.date_of_birth = teacher_form.cleaned_data["date_of_birth"]
            teacher.age = num_years(teacher_form.cleaned_data["date_of_birth"])
            teacher.save()
            group_name = request.POST.get("group_select")
            print(group_name)
            group = Group.objects.get(name=group_name)
            teacher.groups.add(group)
        else:
            print(teacher_form.errors)

    discipline_form = DisciplineNameForm()
    teacher_form = UserForm()
    context = {
        "teacher_form" : teacher_form, 
        "teachers": teachers, 
        "discipline_form": discipline_form, 
        "disciplines_dict": disciplines_dict,
        "disciplines": disciplines,
        "classes": classes
    }
    return render(request, "teachers.html", context=context)


def add_discipline(request):
    if request.method == "POST":
        discipline_form = DisciplineNameForm(request.POST)
        if discipline_form.is_valid():
            discipline_name = request.POST.get("discipline_name")
            discipline = DisciplineName.objects.create(discipline_name=discipline_name)
            discipline.save()
    
    return HttpResponseRedirect("/teachers/")


def add_discipline_to_teacher(request):
    if request.method == "POST":
        teacher_id = request.POST.get("teacher_select")
        teacher = AppUser.objects.get(id=teacher_id)
        discipline_id = request.POST.get("discipline_select")
        discipline = DisciplineName.objects.get(id=discipline_id)
        discipline_teacher = DisciplineTeacher.objects.create(teacher=teacher, discipline=discipline)
        discipline_teacher.save()
    
    return HttpResponseRedirect("/teachers/")


def detach_discipline(request, discipline_record_id):
    discipline_record = get_object_or_404(DisciplineTeacher, id=discipline_record_id)
    discipline_record.delete()
    return HttpResponseRedirect("/")


def students_view(request):
    students_classes = ClassStudent.objects.all().order_by("class_code__class_code", "student__first_name")
    teachers = AppUser.objects.filter(Q(groups__name="teacher") | Q(groups__name="director") | Q(groups__name="head_teacher"))
    classes = ClassCode.objects.all()

    if request.method == "POST":
        student_form = UserForm(request.POST, prefix='student_form')
        mother_form = UserForm(request.POST, prefix="mother_form")
        father_form = UserForm(request.POST, prefix="father_form")
        if student_form.is_valid() and mother_form.is_valid() and father_form.is_valid():
            student = AppUser()
            student.username = student_form.cleaned_data["username"]
            student.set_password(student_form.cleaned_data["password"])
            student.email = student_form.cleaned_data["email"]
            student.first_name = student_form.cleaned_data["first_name"]
            student.last_name = student_form.cleaned_data["last_name"]
            student.patronym = student_form.cleaned_data["patronym"]
            student.date_of_birth = student_form.cleaned_data["date_of_birth"]
            student.age = num_years(student_form.cleaned_data["date_of_birth"])

            mother = AppUser()
            mother.username = mother_form.cleaned_data["username"]
            mother.set_password(mother_form.cleaned_data["password"])
            mother.email = mother_form.cleaned_data["email"]
            mother.first_name = mother_form.cleaned_data["first_name"]
            mother.last_name = mother_form.cleaned_data["last_name"]
            mother.patronym = mother_form.cleaned_data["patronym"]
            mother.date_of_birth = mother_form.cleaned_data["date_of_birth"]
            mother.age = num_years(mother_form.cleaned_data["date_of_birth"])

            father = AppUser()
            father.username = father_form.cleaned_data["username"]
            father.set_password(father_form.cleaned_data["password"])
            father.email = father_form.cleaned_data["email"]
            father.first_name = father_form.cleaned_data["first_name"]
            father.last_name = father_form.cleaned_data["last_name"]
            father.patronym = father_form.cleaned_data["patronym"]
            father.date_of_birth = father_form.cleaned_data["date_of_birth"]
            father.age = num_years(father_form.cleaned_data["date_of_birth"])

            student.save()
            mother.save()
            father.save()

            group = Group.objects.get(name='student')
            student.groups.add(group)
            group = Group.objects.get(name="parent")
            mother.groups.add(group)
            father.groups.add(group)
            class_code = ClassCode.objects.get(id=request.POST.get("class_select"))
            ClassStudent.objects.create(class_code=class_code, student=student)

            Parents.objects.create(student=student, mother=mother, father=father)
        else:
            print("Ученик: " + student_form.errors.as_text())
            print("Мать:" + mother_form.errors.as_text())
            print("Отец:" + father_form.errors.as_text())

    class_code_form = ClassCodeForm()
    student_form = UserForm(prefix="student_form")
    mother_form = UserForm(prefix="mother_form")
    father_form = UserForm(prefix="father_form")
    context = {
        "teachers": teachers,
        "student_form": student_form,
        "mother_form": mother_form,
        "father_form": father_form,
        "class_code_form": class_code_form,
        "students_classes": students_classes,
        "classes": classes
    }
    return render(request, "students.html", context=context)


def add_class(request):
    if request.method == "POST":
        class_code_form = ClassCodeForm(request.POST)
        if class_code_form.is_valid():
            class_code = class_code_form.cleaned_data["class_code"]
            teacher_id = request.POST.get("teacher_select")
            new_class = ClassCode()
            new_class.class_code = class_code
            new_class.homeroom_teacher = AppUser.objects.get(id=teacher_id)
            new_class.save()
    return HttpResponseRedirect('')


def user_info(request, user_id):
    user = AppUser.objects.get(id=user_id)
    context = {}
    context["user"] = user
    group_en = user.groups.get().name
    group = roles_to_russian_dict[group_en]
    context["group"] = group 

    match group_en:
        case "student":
            context["class"] = ClassStudent.objects.get(student = user)
        case "parent":
            context["parents_records"] = Parents.objects.filter(Q(mother = user) | Q(father = user))
        case "teacher" | "director" | "head_teacher":
            context["disciplines"] = DisciplineTeacher.objects.filter(teacher = user)
            context["homeroomed_classes"] = ClassCode.objects.filter(homeroom_teacher = user)

    return render(request, "user_details.html", context)


def user_edit(request, user_id):
    user = AppUser.objects.get(id=user_id)
    context = {}
    context["user_form"] = UserForm(instance=user)
    context["user"] = user
    group_en = user.groups.get().name

    match group_en:
        case "student":
            students_class = ClassStudent.objects.get(student = user)
            context['students_class'] = students_class
            context['classes'] = ClassCode.objects.all().exclude(id=students_class.class_code.id)
        case "parent":
            pass
        case "teacher" | "director" | "head_teacher":
            context['discipline_records'] = DisciplineTeacher.objects.filter(teacher = user)

    return render(request, "user_edit.html", context)

def classes(request):
    classes = ClassCode.objects.all().order_by("class_code")
    teachers = AppUser.objects.filter(Q(groups__name="teacher") | Q(groups__name="director") | Q(groups__name="head_teacher"))
    class_code_form = ClassCodeForm()
    students_classes = ClassStudent.objects.all()
    students_classes_dict = {}

    for students_class in classes:
        if students_class.class_code not in students_classes_dict.keys():
            students_classes_dict[students_class] = []

        records = students_classes.filter(class_code = students_class)
        for record in records:
            students_classes_dict[students_class].append(record.student)

    context = {
        'teachers': teachers,
        'classes': classes,
        'class_code_form': class_code_form,
        'students_classes': students_classes,
        'students_classes_dict': students_classes_dict
    }

    return render(request, "classes.html", context=context)


def class_info(request, class_id):
    students_class = ClassCode.objects.get(id=class_id)
    students_records = ClassStudent.objects.filter(class_code=students_class)

    context = {'students_class': students_class, 'students_records': students_records}
    return render(request, "class_info.html", context)


def class_advance(request, class_id):
    students_class = ClassCode.objects.get(id=class_id)
    integer_code = int(students_class.class_code[:-1])
    if integer_code < 11:
        integer_code += 1
        new_class_code = str(integer_code) + students_class.class_code[-1]
        students_class.class_code = new_class_code
        students_class.save()
    else:
        students_class.status = students_class.GRADUATED
        students_class.graduated_year = datetime.date.today().year
        students_class.save()

    return HttpResponseRedirect("/classes/%d" % class_id)


def all_classes_advance(request):
    students_classes = ClassCode.objects.all().filter(status="ST").order_by("-class_code")

    for students_class in students_classes:
        integer_code = int(students_class.class_code[:-1])
        if integer_code < 11:
            integer_code += 1
            new_class_code = str(integer_code) + students_class.class_code[-1]
            students_class.class_code = new_class_code
            students_class.save()  
        else:
            students_class.status = students_class.GRADUATED
            students_class.graduated_year = datetime.date.today().year
            students_class.save()

    return HttpResponseRedirect("/classes")