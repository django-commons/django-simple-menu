Configuring django-simple-menu
==============================
``django-simple-menu`` has some configuration options that can be configured
in your main `Django settings file`_.

MENU_SELECT_PARENTS
-------------------
**Default: ``False``**

``MENU_SELECT_PARENTS`` controls if parent menu items should automatically have
their ``selected`` property set to ``True`` if one of their children has its
``selected`` property set to ``True``.

MENU_HIDE_EMPTY
-------------------
**Default: ``False``**

``MENU_HIDE_EMPTY`` controls if menu items without an explicit ``check`` callback
should be visible even if they have no children

MENU_TRIM_NON_VISIBLE_CHILD_ITEMS
-------------------
**Default: ``True``**

``MENU_TRIM_NON_VISIBLE_CHILD_ITEMS`` controls if children of menu items should be
removed from the ``item.children`` list if they are not visible. Retaining them
can be useful for breadcrumbs, but can also lead to unexpected results if you do not
check the ``visible`` property of the children in templates.

.. _Django settings file: https://docs.djangoproject.com/en/dev/topics/settings/
