from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(username, email, password, **extra_fields)


class AppUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50, null=True, blank=False)
    last_name = models.CharField(max_length=50, null=True, blank=False)
    patronym = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=50, unique=True)
    age = models.IntegerField(null=True)
    date_of_birth = models.DateTimeField(null=True, blank=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self) -> str:
        return f"{self.last_name} {self.first_name} {self.patronym}"


class Parents(models.Model):
    student = models.OneToOneField(
        AppUser, on_delete=models.CASCADE, related_name="student_to_parents"
    )
    mother = models.ForeignKey(
        AppUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="mother_to_parents",
    )
    father = models.ForeignKey(
        AppUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="father_to_parents",
    )

    class Meta:
        unique_together = (("student", "father", "mother"),)


class DisciplineName(models.Model):
    discipline_name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.discipline_name


class DisciplineTeacher(models.Model):
    discipline = models.ForeignKey(DisciplineName, on_delete=models.CASCADE, related_name="discipline_to_teacher")
    teacher = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="teacher_to_discipline")

    class Meta:
        unique_together = (("teacher", "discipline"),)


class ClassCode(models.Model):
    STUDYING = "ST"
    GRADUATED = "GR"
    STATUS_CHOICES = [
        (STUDYING, "Обучается"),
        (GRADUATED, "Выпущен"),
    ]

    class_code = models.CharField(max_length=3)
    homeroom_teacher = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="homeroom_teacher_to_class")
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=STUDYING)
    graduated_year = models.IntegerField(null=True)

    def clean(self):
        super().clean()
        if self.status == self.STUDYING:
            if (
                ClassCode.objects.filter(
                    class_code=self.class_code, status=self.STUDYING
                )
                .exclude(pk=self.pk)
                .exists()
            ):
                raise ValidationError(
                    "Такой класс уже существует в системе и ещё не выпустился."
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.class_code


class ClassStudent(models.Model):
    class_code = models.ForeignKey(ClassCode, on_delete=models.CASCADE)
    student = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="student_to_class")

    class Meta:
        unique_together = (("class_code", "student"),)


class ClassDisciplines(models.Model):
    class_num = models.SmallIntegerField(null=False, blank=False, unique=True)
    studied_disciplines = models.ManyToManyField(DisciplineName, blank=True)