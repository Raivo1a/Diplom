from django.contrib.auth.models import AbstractUser
from django.db import models


class Employee(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    position = models.CharField(max_length=255, verbose_name="Должность")
    EMPLOYEE_TYPE_CHOICES = (
        ("employee", "Сотрудник"),
        ("manager", "Менеджер"),
    )
    employee_type = models.CharField(
        max_length=20,
        choices=EMPLOYEE_TYPE_CHOICES,
        default="employee",
        verbose_name="Тип сотрудника",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.full_name
