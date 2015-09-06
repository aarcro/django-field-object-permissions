=================================
django-field-object-permissions
=================================
``django-field-object-permissions`` is an object permission system based on
field values of the object. (eg: object.owner == user)

Install
-------
To install just run::

    pip install django-field-object-permissions

Configuration
-------------

1. Put ``fieldobjectpermissions`` to your ``INSTALLED_APPS`` of the settings module::

    INSTALLED_APPS = (
       ...
       'fieldobjectpermissions',
    )

2. Replace the default authentication backend (fieldobjectpermissions is based
on it)::

    AUTHENTICATION_BACKENDS = ('
        # django.contrib.auth.backends.ModelBackend,  # Default
        fieldobjectpermissions.backends.FieldObjectPermissionsBackend',
    )

3. These new values are optional, defaults are shown below::

    FIELD_OBJECT_PERMISSIONS = {
        'OWNER_FIELDS': ('owner',),
        'GROUP_FIELDS': ('group',),
        'OWNER_ACTIONS': ('change', 'delete'),
        'GROUP_ACTIONS': ('change', 'delete'),
    }

4. Run ``python manage.py migrate`` as there are post-migration triggers to create
the extra permissions required.

Usage
-----

You can now assign permissions like ``owner_change_foo`` to allow only the user
who matches the value of the ``owner`` field to change an object (or the
superuser, of course).

Or the permission ``group_delete_foo`` to all allow any user who is a member of
a group listed in the ``group`` field of an object to delete it (or the
superuser, you know this).

These permissions are created in a post-migrate signal handler, and will only
be created for models with have the required field(s).

By specifying multiple fields for ``OWNER_FIELDS`` or ``GROUP_FIELDS`` only one of
the listed fields needs to exist for permission creation. And only one needs
to match for permission to be granted by the auth backend.
