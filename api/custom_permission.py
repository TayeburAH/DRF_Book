from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPostOrIsAuthenticated(BasePermission):
    """
         Global permission check for blocked IPs.
    """

    def has_permission(self, request, view):
        # message =               # denied message
        pass

    # Object-level permission
    """
        Object-level permission to only allow owners of an object to edit it.
        Assumes the model instance has an `owner` attribute.
     """

    def has_object_permission(self, request, view, obj):
        # message =               # denied message
        if request.method in SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user


class ViewCurrentUserOrder(BasePermission):
    def has_object_permission(self, request, view, obj):
        message = "You must be authenticated"  # denied message
        return obj.user == request.user
