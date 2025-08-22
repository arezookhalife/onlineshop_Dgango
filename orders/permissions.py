from rest_framework import permissions

class OrderPermission(permissions.BasePermission):
    def has_permission(self, request, view):

        if request.method in ["GET", "DELETE"]:
            return True

        return request.user.is_staff or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.user == request.user