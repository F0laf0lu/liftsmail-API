from rest_framework import permissions

class IsGroupOwner(permissions.BasePermission):

    def  has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj.group.user == request.user