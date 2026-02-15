from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    message = "Вы не являетесь создателем или исполнителем задачи"

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user == obj.creator:
            return True

        if user == obj.executor:
            if request.method in ["PUT", "PATCH"]:
                allowed_fields = {"status"}
                if set(request.data.keys()).issubset(allowed_fields):
                    return True
                else:
                    return False
            else:
                return True

        return False
