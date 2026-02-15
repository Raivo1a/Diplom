from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from employee.models import Employee
from task.models import Task

User = get_user_model()


class BusyEmployeesAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.emp1 = Employee.objects.create(
            email="ivan@example.com", full_name="Ivan Ivanov"
        )
        self.emp2 = Employee.objects.create(
            email="petr@example.com", full_name="Petr Petrov"
        )
        self.emp3 = Employee.objects.create(
            email="sidor@example.com", full_name="Sidor Sidorov"
        )

        now = timezone.now()

        Task.objects.create(
            executor=self.emp1, status="in_progress", deadline=now + timedelta(days=1)
        )
        Task.objects.create(
            executor=self.emp1, status="completed", deadline=now + timedelta(days=2)
        )
        Task.objects.create(
            executor=self.emp2, status="in_progress", deadline=now + timedelta(days=3)
        )
        Task.objects.create(
            executor=self.emp2, status="in_progress", deadline=now + timedelta(days=3)
        )
        Task.objects.create(
            executor=self.emp3, status="completed", deadline=now + timedelta(days=4)
        )

    def test_busy_employees(self):
        """
        Тестирует эндпоинт, который возвращает список сотрудников с количеством их активных задач
        (статус 'in_progress'), упорядоченный по убыванию количества активных задач.
        """
        self.client.force_authenticate(user=self.emp1)

        url = reverse("employee:busy_employees")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        print(data)
        self.assertEqual(len(data), 3)

        self.assertEqual(data[0]["full_name"], "Petr Petrov")
        self.assertEqual(data[0]["active_tasks"], 2)

        self.assertEqual(data[1]["full_name"], "Ivan Ivanov")
        self.assertEqual(data[1]["active_tasks"], 1)

        self.assertEqual(data[2]["full_name"], "Sidor Sidorov")
        self.assertEqual(data[2]["active_tasks"], 0)
