from rest_framework.permissions import IsAuthenticated


class FilePermissions(IsAuthenticated):

    def has_permission(self, request, view):
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        permissions_ok = obj.permission == '' or request.user.has_perm(obj.permission)
        is_owner = obj.username == request.user.username
        return request.user.is_superuser or is_owner or (obj.share and permissions_ok)
