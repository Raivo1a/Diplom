from django.db.models import Count, Q
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from employee.models import Employee
from employee.serializers import EmployeeSerializer


class EmployeeCreateAPIView(generics.CreateAPIView):
    """Создание нового сотрудника"""

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [AllowAny]


class EmployeeListAPIView(generics.ListAPIView):
    """Список сотрудников"""

    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()
    permission_classes = [IsAuthenticated]
    ordering = ["-count_tasks"]


class EmployeeRetrieveAPIView(generics.RetrieveAPIView):
    """Данные одного сотрудника"""

    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()
    permission_classes = [IsAuthenticated]


class EmployeeUpdateAPIView(generics.UpdateAPIView):
    """Обновление сотрудника"""

    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()
    permission_classes = [IsAuthenticated]


class EmployeeDestroyAPIView(generics.DestroyAPIView):
    """Удаление сотрудника"""

    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()
    permission_classes = [IsAuthenticated]


@api_view(["GET"])
def busy_employees(request):
    """Список сотрудников по количеству активных задач"""
    employees = Employee.objects.annotate(
        active_tasks=Count("tasks", filter=Q(tasks__status="in_progress"))
    ).order_by("-active_tasks")
    data = [
        {"full_name": emp.full_name, "active_tasks": emp.active_tasks}
        for emp in employees
    ]
    return Response(data)
