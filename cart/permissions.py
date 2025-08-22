from rest_framework import permissions

class IsCartOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user.is_superuser or obj.cart.user == request.user