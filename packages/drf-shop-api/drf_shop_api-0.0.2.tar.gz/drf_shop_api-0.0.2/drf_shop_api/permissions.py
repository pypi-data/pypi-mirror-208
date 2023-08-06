from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """IsAdminOrReadOnly

    This allows only admin users to create site wide objects
    All other users can only use safe methods

    """

    def has_permission(self, request, view):
        return request.user.is_staff or request.method in ["GET", "HEAD", "OPTIONS"]


class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):
    """IsAdminOrAuthorOrReadOnly

    This allows only admin users to create site wide objects, and author users
    All other users can only use safe methods

    """

    def has_permission(self, request, view):
        # Updating as author
        is_author = False
        if target := view.queryset.filter(pk=view.kwargs.get("pk")).first():
            is_author = target.user == request.user

        return request.user.is_staff or is_author or request.method in ["GET", "HEAD", "OPTIONS"]


class GetByAnyCreateByAuthEditByOwner(permissions.BasePermission):
    """GetByAnyCreateByAuthEditByAuthor
    This allows creation by any user
    editing only by author
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        return obj.user == request.user

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class GetByAuthOrAdminEditByAdmin(permissions.BasePermission):
    """GetByAnyCreateByAuthEditByAuthor"""

    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"] and request.user.is_authenticated:
            return True
        return obj.user == request.user

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class GetByAuthOrAdminEditByOwner(permissions.BasePermission):
    """GetByAnyCreateByAuthEditByAuthor"""

    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"] and request.user.is_authenticated:
            return True
        return obj.user == request.user

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
