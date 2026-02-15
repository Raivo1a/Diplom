from django.core.management import BaseCommand

from employee.models import Employee


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = Employee.objects.create(email="admin@example.com")
        user.set_password("1234")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
