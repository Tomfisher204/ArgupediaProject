from rest_framework.permissions import IsAuthenticated

class IsAdminPermission(IsAuthenticated):
    """Grants access only to authenticated users who have is_admin=True."""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_admin