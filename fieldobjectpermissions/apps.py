from django.apps import apps, AppConfig
from django.conf import settings
from django.contrib.auth import get_permission_codename
from django.core import exceptions
from django.db import DEFAULT_DB_ALIAS, router
from django.db.models.fields import FieldDoesNotExist
from django.db.models.signals import post_migrate

from .backends import GROUP_FIELDS, OWNER_FIELDS, GROUP_ACTIONS, OWNER_ACTIONS


def _get_extra_permissions(opts, ctype):
    new_perms = []

    for field in GROUP_FIELDS:
        try:
            opts.get_field(field)
        except FieldDoesNotExist:
            pass
        else:
            for action in GROUP_ACTIONS:
                action = 'group_' + action
                new_perms.append((
                    get_permission_codename(action, opts),
                    'Can %s %s' % (action, opts.verbose_name_raw)
                ))

            # Only need one match to create the perm
            break

    for field in OWNER_FIELDS:
        try:
            opts.get_field(field)
        except FieldDoesNotExist:
            pass
        else:
            for action in OWNER_ACTIONS:
                action = 'owner_' + action
                new_perms.append((
                    get_permission_codename(action, opts),
                    'Can %s %s' % (action, opts.verbose_name_raw)
                ))
            # Only need one match to create the perm
            break

    return new_perms


# Cribbed from django.contrib.auth.management.__init__
def create_permissions(app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, **kwargs):
    """Create additional group and own permissions when possible, with some exclusions
    """
    if not app_config.models_module:
        return

    try:
        Permission = apps.get_model('auth', 'Permission')
    except LookupError:
        return

    # Handle django 1.7 and 1.8
    for meth in ('allow_migrate', 'allow_migrate_model'):
        if hasattr(router, meth):
            break

    if not getattr(router, meth)(using, Permission):
        return

    from django.contrib.contenttypes.models import ContentType

    permission_name_max_length = Permission._meta.get_field('name').max_length
    # TODO - calculate from the action USER/GROUP_ACTIONS
    verbose_name_max_length = permission_name_max_length - 17  # len('Can group_change ') prefix

    # This will hold the permissions we're looking for as
    # (content_type, (codename, name))
    searched_perms = list()
    # The codenames and ctypes that should exist.
    ctypes = set()
    for klass in app_config.get_models():
        # TODO - Black list some models, like User and Group

        # Force looking up the content types in the current database
        # before creating foreign keys to them.
        ctype = ContentType.objects.db_manager(using).get_for_model(klass)

        if len(klass._meta.verbose_name) > verbose_name_max_length:
            raise exceptions.ValidationError(
                "The verbose_name of %s.%s is longer than %s characters" % (
                    ctype.app_label,
                    ctype.model,
                    verbose_name_max_length,
                )
            )

        ctypes.add(ctype)
        for perm in _get_extra_permissions(klass._meta, ctype):
            searched_perms.append((ctype, perm))

    # Find all the Permissions that have a content_type for a model we're
    # looking for.  We don't need to check for codenames since we already have
    # a list of the ones we're going to create.
    all_perms = set(Permission.objects.using(using).filter(
        content_type__in=ctypes,
    ).values_list(
        "content_type", "codename"
    ))

    perms = [
        Permission(codename=codename, name=name, content_type=ct)
        for ct, (codename, name) in searched_perms
        if (ct.pk, codename) not in all_perms
    ]
    # Validate the permissions before bulk_creation to avoid cryptic database
    # error when the name is longer than 255 characters
    for perm in perms:
        if len(perm.name) > permission_name_max_length:
            raise exceptions.ValidationError(
                "The permission name %s of %s.%s is longer than %s characters" % (
                    perm.name,
                    perm.content_type.app_label,
                    perm.content_type.model,
                    permission_name_max_length,
                )
            )
    Permission.objects.using(using).bulk_create(perms)
    if verbosity >= 2:
        for perm in perms:
            print("Adding permission '%s'" % perm)


class FieldObjectPermissionsConfig(AppConfig):
    name = 'fieldobjectpermissions'
    verbose_name = 'Field Object Permissions'

    def ready(self):
        post_migrate.connect(
            create_permissions,
            dispatch_uid='fieldobjectpermissions.create_permissions',
        )
