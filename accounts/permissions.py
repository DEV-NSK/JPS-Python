from rest_framework.permissions import BasePermission


class IsEmployer(BasePermission):
    message = 'Employer access only'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'employer')


class IsAdmin(BasePermission):
    message = 'Admin access only'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


class IsEmployerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            request.user.role in ('employer', 'admin')
        )
