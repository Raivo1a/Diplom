from django.urls import path

from .apps import EmployeeConfig
from .views import (EmployeeCreateAPIView, EmployeeDestroyAPIView,
                    EmployeeListAPIView, EmployeeRetrieveAPIView,
                    EmployeeUpdateAPIView, busy_employees)

app_name = EmployeeConfig.name


urlpatterns = [
    path("", EmployeeListAPIView.as_view(), name="employee_list"),
    path("create/", EmployeeCreateAPIView.as_view(), name="employee_create"),
    path(
        "<int:pk>/update/",
        EmployeeUpdateAPIView.as_view(),
        name="employee_update",
    ),
    path(
        "<int:pk>/retrieve/",
        EmployeeRetrieveAPIView.as_view(),
        name="employee_retrieve",
    ),
    path(
        "<int:pk>/destroy/",
        EmployeeDestroyAPIView.as_view(),
        name="employee_destroy",
    ),
    path("busy_employees/", busy_employees, name="busy_employees"),
]
