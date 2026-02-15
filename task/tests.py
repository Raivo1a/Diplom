from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Task

User = get_user_model()


class TaskTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="test@test.com", employee_type="manager")
        self.client = APIClient()
        self.admin_user = User.objects.create(
            email="admin@test.com",
            employee_type="manager",
            is_staff=True,
            is_superuser=True,
        )

        self.task = Task.objects.create(
            name="Test Task",
            description="Description",
            status="not_started",
            deadline=timezone.now().date() + timedelta(days=5),
            executor=None,
            creator=self.user,
        )

    def test_create_task(self):
        """Тест на создание новой задачи. Проверяет успешную отправку POST-запроса и увеличение количества задач"""
        data = {
            "name": "New Task",
            "description": "Test description",
            "status": "not_started",
            "deadline": (timezone.now().date() + timedelta(days=3)),
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/tasks/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_list_tasks_marks_failed_when_deadline_passed(self):
        """Проверяет автоматическую смену статуса задачи на 'failed', если дедлайн прошел, и возвращает список задач"""
        self.task.deadline = timezone.now().date() - timedelta(days=1)
        self.task.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "failed")
        self.assertIn(self.task.name, [item["name"] for item in response.data])

    def test_update_task(self):
        """Тестирует обновление существующей задачи. Проверяет, что изменения сохраняются корректно"""
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Updated Task Name",
            "status": "not_started",
            "deadline": self.task.deadline,
        }
        response = self.client.put(f"/tasks/{self.task.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, "Updated Task Name")

    def test_delete_task_as_admin(self):
        """
        Проверяет возможность удаления задачи при выполнении запроса администратором.
        Удостоверяется, что задача удалена и возвращается правильный код статуса.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f"/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())


class ImportantTasksTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            email="test@example.com", full_name="Иван Иванов", employee_type="manager"
        )

        self.root_task = Task.objects.create(
            name="Главная задача",
            executor=self.user,
            deadline=date(2023, 12, 31),
            status="in_progress",
        )

        self.target_task = Task.objects.create(
            name="Важная подзадача",
            parent_task=self.root_task,
            executor=self.user,
            deadline=date(2023, 12, 1),
            status="not_started",
        )

        self.child_task = Task.objects.create(
            name="Дочерняя задача в процессе",
            parent_task=self.target_task,
            executor=self.user,
            deadline=date(2023, 12, 5),
            status="in_progress",
        )

        self.wrong_status_task = Task.objects.create(
            name="Задача со статусом в процессе",
            parent_task=self.root_task,
            executor=self.user,
            deadline=date(2023, 12, 1),
            status="in_progress",
        )

        self.no_parent_task = Task.objects.create(
            name="Нет родительской задачи",
            executor=self.user,
            deadline=date(2023, 12, 1),
            status="not_started",
        )

        self.url = reverse("task:important_tasks")

    def test_get_important_tasks_success(self):
        """
        Проверяет успешное получение списка важных задач.
        Убеждается, что фильтрация работает: возвращается только нужная задача.
        Проверяет, что запрошенная задача содержит правильные поля.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)

        task_data = response.data[0]
        self.assertEqual(task_data["task_name"], self.target_task.name)
        self.assertEqual(task_data["deadline"], self.target_task.deadline)
        self.assertEqual(task_data["employee_full_name"], self.user.full_name)

    def test_filter_logic(self):
        """Проверяет, что задачи без дочерних задач со статусом 'in_progress' не попадают в список важных задач"""
        self.client.force_authenticate(user=self.user)

        self.child_task.status = "completed"
        self.child_task.save()

        response = self.client.get(self.url)

        self.assertEqual(len(response.data), 0)

    def test_no_tasks_when_conditions_not_met(self):
        """
        Проверяет, что при выполнении условий фильтрации задач список пуст.
        Возвращает пустой массив, если задача не соответствует критериям
        """
        self.client.force_authenticate(user=self.user)

        self.child_task.status = "completed"
        self.child_task.save()

        url = reverse("task:important_tasks")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
