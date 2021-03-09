from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.groups.filter(name='admin').exists()

class IsAgent(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.groups.filter(name='agent').exists()