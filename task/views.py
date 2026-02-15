from django.db.models import Count, Min, Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from employee.models import Employee
from permissions import IsOwner

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        """Создать задачу, если пользователь — менеджер"""
        user = self.request.user
        if user.employee_type == "manager":
            serializer.save(creator=user)
        else:
            raise PermissionDenied("Только менеджеры могут создавать задания")

    def check_and_update_task_status(self, task):
        """Обновить статус задачи на failed, если просрочен дедлайн"""
        if (
            task.status not in ["completed", "failed"]
            and task.deadline < timezone.now().date()
        ):
            task.status = "failed"
            task.save()
            return True
        else:
            return True

    def list(self, request, *args, **kwargs):
        """Получить список задач с обновлением статуса"""
        queryset = self.filter_queryset(self.get_queryset())
        serializers = []
        for task in queryset:
            if self.check_and_update_task_status(task):
                serializer = self.get_serializer(task)
                serializers.append(serializer.data)
        return Response(serializers)

    def perform_update(self, serializer):
        """Обновить задачу и перевести в in_progress, если назначен исполнитель"""
        task = serializer.save()
        if task.status == "not_started" and task.executor is not None:
            task.status = "in_progress"
            task.save()

    def get_permissions(self):
        """Определить права доступа для каждого действия"""
        if self.action == "create":
            permission_classes = [IsAuthenticated]
        elif self.action == "retrieve":
            permission_classes = [IsAuthenticated, IsOwner | IsAdminUser]
        elif self.action == "destroy":
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action == "update":
            permission_classes = [IsAuthenticated, IsOwner | IsAdminUser]
        else:
            permission_classes = [IsAuthenticated | IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsOwner]
    )
    def complete(self, request, pk=None):
        """Отметить задачу как выполненную"""
        task = self.get_object()
        user = request.user
        if user != task.executor and not user.employee_type == "manager":
            return Response(
                {"detail": "Нет прав на выполнение этой задачи"}, status=403
            )
        if task.status == "completed":
            return Response({"detail": "Задача уже выполнена"}, status=400)

        task.status = "completed"
        task.save()
        return Response({"status": "Задача выполнена"})


@api_view(["GET"])
def important_tasks(request):
    """Список важных задач с назначением на наименее загруженного сотрудника"""
    important_tasks_qs = Task.objects.filter(
        status="not_started", dependent_tasks__status="in_progress"
    ).distinct()
    employee_tasks_counts = Employee.objects.annotate(
        in_progress_tasks=Count("tasks", filter=Q(tasks__status="in_progress"))
    )
    min_in_progress = employee_tasks_counts.aggregate(Min("in_progress_tasks"))[
        "in_progress_tasks__min"
    ]
    if min_in_progress is None:
        min_in_progress = 0

    least_loaded_employees = employee_tasks_counts.filter(
        in_progress_tasks=min_in_progress
    )
    least_loaded_employee = least_loaded_employees.first()

    results = []
    for task in important_tasks_qs:
        parent_executor = None
        if task.parent_task and task.parent_task.executor:
            parent_executor = task.parent_task.executor
            parent_executor_load = (
                employee_tasks_counts.filter(id=parent_executor.id)
                .first()
                .in_progress_tasks
            )
        else:
            parent_executor_load = None

        if parent_executor and parent_executor_load <= (min_in_progress + 2):
            chosen_employee = parent_executor
        else:
            chosen_employee = least_loaded_employee

        results.append(
            {
                "task_name": task.name,
                "deadline": task.deadline,
                "employee_full_name": (
                    chosen_employee.full_name if chosen_employee else None
                ),
            }
        )

    return Response(results)
