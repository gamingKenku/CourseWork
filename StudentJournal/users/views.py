from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from users.forms import LoginForm, UserForm, DisciplineNameForm, ClassCodeForm
from users.models import AppUser, DisciplineName, DisciplineTeacher, ClassCode, ClassStudent, Parents
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from users.methods.defs import num_years
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
            teacher = teacher_form.save()
            
            group_name = request.POST.get("group_select")
            print(group_name)
            group = Group.objects.get(name=group_name)
            teacher.groups.add(group)
        else:
            print(teacher_form.errors)
            request.session['teacher_form_post_data'] = request.POST

    if 'teacher_form_post_data' in request.session:
        teacher_form = UserForm(request.session['teacher_form_post_data'])
        del request.session['teacher_form_post_data']
    else:
        teacher_form = UserForm

    discipline_form = DisciplineNameForm()
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
        student_form = UserForm(request.POST, prefix="student_form")
        mother_form = UserForm(request.POST, prefix="mother_form")
        father_form = UserForm(request.POST, prefix="father_form")

        if student_form.is_valid() and mother_form.is_valid() and father_form.is_valid():
            usernames_valid = True
            emails_valid = True
            student = student_form.save(commit=False)
            mother = mother_form.save(commit=False)
            father = father_form.save(commit=False)

            if len(set([student.username, mother.username, father.username])) < 3:
                usernames_valid = False
                request.session['student_form_post_data'] = request.POST
                student_form.add_error("username", "Имена пользователей должны быть разными.")
                mother_form.add_error("username", "Имена пользователей должны быть разными.")
                father_form.add_error("username", "Имена пользователей должны быть разными.")
            
            if len(set([student.email, mother.email, father.email])) < 3:
                emails_valid = False
                request.session['student_form_post_data'] = request.POST
                student_form.add_error("email", "Адреса электронных почт должны быть разными.")
                mother_form.add_error("email", "Адреса электронных почт должны быть разными.")
                father_form.add_error("email", "Адреса электронных почт должны быть разными.")

            if usernames_valid and emails_valid:
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
            request.session['student_form_post_data'] = request.POST

        print(student_form.errors)
        print(mother_form.errors)
        print(father_form.errors)

    if 'student_form_post_data' in request.session and (student_form.errors or mother_form.errors or father_form.errors):
        student_form = UserForm(request.session['student_form_post_data'], prefix="student_form")
        mother_form = UserForm(request.session['student_form_post_data'], prefix="mother_form")
        father_form = UserForm(request.session['student_form_post_data'], prefix="father_form")        
        del request.session['student_form_post_data']
    else:
        student_form = UserForm(prefix="student_form")
        mother_form = UserForm(prefix="mother_form")
        father_form = UserForm(prefix="father_form")

    class_code_form = ClassCodeForm()
    
    context = {
        "teachers": teachers,
        "student_form" : student_form,
        "mother_form" : mother_form,
        "father_form" : father_form,
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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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