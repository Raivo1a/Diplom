from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .apps import TaskConfig
from .views import TaskViewSet, important_tasks

app_name = TaskConfig.name

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("important_tasks/", important_tasks, name="important_tasks"),
]
