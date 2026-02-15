from django.db import models

from employee.models import Employee


class Task(models.Model):
    name = models.CharField(max_length=255, verbose_name="Наименование")
    description = models.CharField(max_length=255, null=True, blank=True)
    parent_task = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="dependent_tasks",
    )
    executor = models.ForeignKey(
        Employee, related_name="tasks", on_delete=models.CASCADE, null=True, blank=True
    )
    creator = models.ForeignKey(
        Employee, on_delete=models.CASCADE, null=True, blank=True
    )
    deadline = models.DateField(verbose_name="Дэдлайн")
    status_choices = [
        ("not_started", "Не начато"),
        ("in_progress", "В процессе"),
        ("completed", "Завершено"),
        ("failed", "Провалено"),
    ]
    status = models.CharField(max_length=20, choices=status_choices)
    created_at = models.DateField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    def __str__(self):
        return self.name
