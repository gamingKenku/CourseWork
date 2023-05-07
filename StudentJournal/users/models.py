from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from datetime import date


class UserManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        name = 'admin'
        age = 100
        dob = date.today()
        user = self.model(username=username, first_name=name, last_name=name,
                          email=email, age=age, date_of_birth=dob, **extra_fields)
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
    email = models.EmailField(max_length=50)
    age = models.IntegerField(validators=[MinValueValidator(6), MaxValueValidator(100)])
    date_of_birth = models.DateTimeField()
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['email']


class Parents(models.Model):
    student = models.OneToOneField(AppUser, on_delete=models.CASCADE, related_name="student_to_parents")
    mother = models.ForeignKey(AppUser, on_delete=models.CASCADE, null=True, blank=True, related_name="mother_to_parents")
    father = models.ForeignKey(AppUser, on_delete=models.CASCADE, null=True, blank=True, related_name="father_to_parents")

    class Meta:
        unique_together = (('student', 'father', 'mother'),)


class ClassCode(models.Model):
    STUDYING = "ST"
    GRADUATED = "GR"
    STATUS_CHOICES = [
        (STUDYING, "Обучается"),
        (GRADUATED, "Выпущен"),
    ]

    class_code = models.CharField(max_length=5)
    homeroom_teacher = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=2,
        choices=STATUS_CHOICES,
        default=STUDYING)
    graduated_year = models.IntegerField(null=True)

    def clean(self):
        super().clean()
        if self.status == self.STUDYING:
            # Check if there are other records with the same class_code and status='ST'
            if ClassCode.objects.filter(class_code=self.class_code, status=self.STUDYING).exclude(pk=self.pk).exists():
                raise ValidationError("There can only be one record with the same class code and status 'ST'.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class ClassStudent(models.Model):
    class_code = models.ForeignKey(ClassCode, on_delete=models.CASCADE)
    student = models.ForeignKey(AppUser, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('class_code', 'student'),)
        ordering = ["class_code"]


class DisciplineName(models.Model):
    discipline_name = models.CharField(max_length=50, unique=True)


class DisciplineTeacher(models.Model):
    discipline = models.ForeignKey(DisciplineName, on_delete=models.CASCADE)
    teacher = models.ForeignKey(AppUser, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('teacher', 'discipline'),)