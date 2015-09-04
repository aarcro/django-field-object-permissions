from django.contrib.auth.backends import ModelBackend
from django.conf import settings

# TODO - Refactor to allow more different fields/permissions
my_settings = getattr(settings, 'FIELD_OBJECT_PERMISSIONS', {})
GROUP_FIELDS = my_settings.get('GROUP_FIELDS', ('group',))
OWNER_FIELDS = my_settings.get('OWNER_FIELDS', ('owner',))

GROUP_ACTIONS = my_settings.get('GROUP_ACTIONS', ('change', 'delete'))
OWNER_ACTIONS = my_settings.get('OWNER_ACTIONS', ('change', 'delete'))


class FieldObjectPermissionsBackend(ModelBackend):
    """Extends ModelBackend to Implement object level permissions bassed on
    alternate permission names and particular relations.

    Example: If testing for app.view_model, the User will be authorized if one
    of the following conditions is met:

    1. The user has app.view_model permission.
    2. The user has app.group_view_model permission,
       and the user's groups contains one of the object's GROUP_FIELDS
    3. The user has app.owner_view_model permission,
       and one of the object's OWNER_FIELDS matches the user.

    Note: This replaces the default ModelBackend, there is no need to specify
    both in AUTHENTICATION_BACKENDS.
    """

    def has_perm(self, user, perm, obj=None):
        super_self = super(ModelBackend, self)
        if super_self.has_perm(user, perm, obj):
            return True

        # look for the extra group or own versions of the permission
        # {group,own}_add_foo doesn't make sense, but no harm in checking it.
        # Assume perm is <app>.<action> format

        try:
            app, action = perm.split('.', 1)
        except ValueError:
            return False  # Can't judge if perm in the wrong format

        if super_self.has_perm(user, '{}.group_{}'.format(app, action), obj):
            # Do have the group perm, check the group

            try:
                # If any of a user's groups match the required fields on the object
                if user.groups.filter(pk__in=[getattr(obj, field).pk for field in GROUP_FIELDS]):
                    return True
            except AttributeError:
                pass  # user or obj missing group relation, try owner

        if super_self.has_perm(user, '{}.owner_{}'.format(app, action), obj):
            # Do have the own perm, check the OWNER_FIELDS
            for field in OWNER_FIELDS:
                if getattr(field, obj, None) == user:
                    return True

        return False  # Didn't have group or own perm
