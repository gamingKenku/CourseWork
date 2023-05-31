from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from users.forms import LoginForm, UserForm, DisciplineNameForm, ClassCodeForm, ClassDisciplinesForm
from users.models import AppUser, DisciplineName, DisciplineTeacher, ClassCode, ClassStudent, Parents, ClassDisciplines
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from users.methods.defs import num_years
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
import datetime


roles_to_russian_dict = {
    "student": "ученик",
    "teacher": "учитель",
    "head_teacher": "завуч",
    "director": "директор",
    "parent": "родитель"
}


@login_required(login_url="/login/")
def index(request):
    context = {}
    return render(request, "index.html", context)


def login_user(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect("/")
            else:
                form.add_error(None, "Неправильное имя пользователя или пароль.")
    else:
        form = LoginForm()

    return render(request, 'login.html', context={"form": form})


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect("/login/")


@login_required(login_url="/login/")
def account(request):
    return render(request, "account.html", context={})


@login_required(login_url="/login/")
@permission_required("users.view_appuser", "/login/")
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
            group = Group.objects.get(name=group_name)
            teacher.groups.add(group)

            return HttpResponseRedirect("/teachers/")
    else:
        teacher_form = UserForm()

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


@login_required(login_url="/login/")
@permission_required("users.add_disciplinename", "/login/")
def add_discipline(request):
    if request.method == "POST":
        discipline_form = DisciplineNameForm(request.POST)
        if discipline_form.is_valid():
            discipline_name = discipline_form.cleaned_data.get("discipline_name")
            discipline = DisciplineName.objects.create(discipline_name=discipline_name)
            discipline.save()
    
    return HttpResponseRedirect("/teachers/")


@login_required(login_url="/login/")
@permission_required("users.add_disciplineteacher", "/login/")
def add_discipline_to_teacher(request):
    if request.method == "POST":
        teacher_id = request.POST.get("teacher_select")
        teacher = AppUser.objects.get(id=teacher_id)
        discipline_id = request.POST.get("discipline_select")
        discipline = DisciplineName.objects.get(id=discipline_id)
        DisciplineTeacher.objects.get_or_create(teacher=teacher, discipline=discipline)
    
    return HttpResponseRedirect("/teachers/")


@login_required(login_url="/login/")
@permission_required("users.delete_disciplineteacher", "/login/")
def detach_discipline(request, discipline_record_id):
    discipline_record = get_object_or_404(DisciplineTeacher, id=discipline_record_id)
    discipline_record.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url="/login/")
@permission_required("users.view_appuser", "/login/")
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
                student_form.add_error("username", "Имена пользователей должны быть разными.")
                mother_form.add_error("username", "Имена пользователей должны быть разными.")
                father_form.add_error("username", "Имена пользователей должны быть разными.")
            
            if len(set([student.email, mother.email, father.email])) < 3:
                emails_valid = False
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

            return HttpResponseRedirect("/students/")
    else:
        student_form = UserForm(prefix="student_form")
        mother_form = UserForm(prefix="mother_form")
        father_form = UserForm(prefix="father_form")

    class_code_form = ClassCodeForm()
    
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


@login_required(login_url="/login/")
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


@login_required(login_url="/login/")
@permission_required("users.change_appuser", "/login/")
def user_edit(request, user_id):
    user = AppUser.objects.get(id=user_id)
    context = {}
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

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        
        if user_form.is_valid():
            user_form.save()
            if group_en == "student":
                students_class.class_code = ClassCode.objects.get(id=request.POST["class_select"])
                students_class.save()
        return HttpResponseRedirect(f"/users/{user_id}/")

    else:
        user_form = UserForm(instance=user)

    context["user_form"] = user_form
    
    return render(request, "user_edit.html", context)


@login_required(login_url="/login/")
@permission_required("users.view_classcode", "/login/")
def classes(request):
    classes = ClassCode.objects.all().order_by("class_code")
    teachers = AppUser.objects.filter(Q(groups__name="teacher") | Q(groups__name="director") | Q(groups__name="head_teacher"))
    students_classes = ClassStudent.objects.all()
    students_classes_dict = {}

    if request.method == "POST":
        class_code_form = ClassCodeForm(request.POST)
        if class_code_form.is_valid():
            class_code = class_code_form.cleaned_data["class_code"]
            teacher_id = request.POST.get("teacher_select")
            new_class = ClassCode()
            new_class.class_code = class_code
            new_class.homeroom_teacher = AppUser.objects.get(id=teacher_id)
            new_class.save()
    else:
        class_code_form = ClassCodeForm()

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


@login_required(login_url="/login/")
@permission_required("users.view_classcode", "/login/")
def class_info(request, class_id):
    students_class = ClassCode.objects.get(id=class_id)
    students_records = ClassStudent.objects.filter(class_code=students_class)

    context = {'students_class': students_class, 'students_records': students_records}
    return render(request, "class_info.html", context)


@login_required(login_url="/login/")
@permission_required("users.change_classcode", "/login/")
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


@login_required(login_url="/login/")
@permission_required("scheduling.change_classcode", "/login/")
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


@login_required(login_url="/login/")
@permission_required("users.change_disciplineteacher", "/login/")
def studied_disciplines(request, class_num):
    class_disciplines_instance = ClassDisciplines.objects.get_or_create(class_num=class_num)[0]
    
    if request.method == "POST":
        form = ClassDisciplinesForm(request.POST, instance=class_disciplines_instance)
        
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/classes/")
    else:
        form = ClassDisciplinesForm(instance=class_disciplines_instance)
        form.fields["class_num"].initial = class_num

    context = {
        "form": form
    }

    return render(request, "studied_disciplines.html", context)