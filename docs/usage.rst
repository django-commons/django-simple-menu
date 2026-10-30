Using django-simple-menu
========================

Usage Overview
--------------

``django-simple-menu`` lets you define multiple different menus that you can
access from within your templates. This way you can have a menu for your main
navigation, another menu for logged in users, another menu for anonymous users,
etc.

To define your menus you need to create a file named ``menus.py`` inside of the
app that you wish to hook menus up to. In the ``menus.py`` file you should
import the ``Menu`` and ``MenuItem`` classes from the ``simple_menu`` package::

    from simple_menu import Menu, MenuItem

The ``Menu`` class exposes a class method named ``add_item`` that accepts two
arguments; the menu name you want to add to, and the ``MenuItem`` you're going
to add.

The ``MenuItem`` class should be instantiated and passed to the ``add_item``
class method with the appropriate parameters. ``MenuItem`` accepts a wide
number of options to its constructor method, the majority of which are simply
attributes that become available in your templates when you're rendering out
the menus.

``MenuItem`` requires the first two arguments:

 * The ``title`` of the item
 * The ``url`` of the item, which can be a string or a callable which accepts the request
 object and returns a string.

The keywords that affect menu generation are:

* The ``weight`` keyword argument affects sorting of the menu.
* The ``children`` keyword argument is either a list of ``MenuItem`` objects,
  or a callable which accepts the request object and returns a list.
* The ``check`` keyword argument is a callable that accepts the request object
  and returns ``True`` or ``False`` if the ``MenuItem`` should be visible for
  this request

Additional kwargs can be passed to ``MenuItem`` and these will become
available in your templates. For example adding ``separator=True`` could be
used to add separators to menus ``{% if item.separator %}<li
class="divider"></li>{% endif %}``

For the full list of ``MenuItem`` options see the
`simple_menu __init__.py source file`_.

Usage Example
-------------

Example::

    # Add two items to our main menu
    Menu.add_item("main", MenuItem("Tools",
                                   reverse("myapp.views.tools"),
                                   weight=10,
                                   icon="tools"))

    Menu.add_item("main", MenuItem("Reports",
                                   reverse("myapp.views.reports"),
                                   weight=20,
                                   icon="report"))


    # Define children for the my account menu
    myaccount_children = (
        MenuItem("Edit Profile",
                 reverse("accounts.views.editprofile"),
                 weight=10,
                 icon="user"),
        MenuItem("Admin",
                 reverse("admin:index"),
                 weight=80,
                 separator=True,
                 check=lambda request: request.user.is_superuser),
        MenuItem("Logout",
                 reverse("accounts.views.logout"),
                 weight=90,
                 separator=True,
                 icon="user"),
    )

    # Add a My Account item to our user menu
    Menu.add_item("user", MenuItem("My Account",
                                   reverse("accounts.views.myaccount"),
                                   weight=10,
                                   children=myaccount_children))


Once you have your menus defined you need to incorporate them into your
templates. This is done through the ``generate_menu`` template tag::

    {% extends "base.html" %}
    {% load simple_menu %}

    {% block content %}
    {% generate_menu %}
    ...
    {% endblock %}

Note that ``generate_menu`` must be called inside of a block.

Once you call ``generate_menu`` all of your MenuItems will be evaluated and
the following items will be set in the context for you.

#. ``menus`` - This is an object that contains all of the lists of menus as
   attribute names::

       {% for item in menus.user %} ... {% endfor %}

#. ``selected_menu`` - This is the ``MenuItem`` object of the most specific
   URL match.
#. ``submenu`` - This is the submenu object of the most specific URL match.
#. ``has_submenu`` - This is ``True`` or ``False`` if the selected menu has
   children.


See the bootstrap-navbar.html file in the templates dir of the source code for
an example that renders menus for the `Bootstrap Navbar Component`_.
You can use it like::

    {% with menu=menus.main %}{% include "bootstrap-navbar.html" %}{% endwith %}


Internacionalization
--------------------

If your project uses ``i18n_patterns`` for handling localized URLs, you should define the ``url``
argument in ``MenuItem`` as a callable instead of a static string. This ensures that the correct
localized URL is resolved based on the active language.

For example, consider the following implementation inside a ``utils/menus.py`` file:

``utils/menus.py``::

    from django.urls import reverse
    from django.utils.translation import gettext_lazy as _
    from simple_menu import Menu, MenuItem

    Menu.add_item(
        "main",
        MenuItem(
            _("Awesome App"),  # Title translated using gettext_lazy
            lambda request: reverse("portal:index"),  # URL resolved dynamically
            icon="fa-solid fa-circle",
            check=lambda request: request.user.is_authenticated,
        ),
    )

When using ``i18n_patterns``, Django assigns language-specific prefixes to URLs (e.g., ``/en/portal/index/`` for English and ``/fr/portal/index/`` for French). By defining the ``url`` as a callable (``lambda request: reverse("portal:index")``), Django ensures that it resolves the correct localized URL dynamically at runtime, rather than hardcoding it.


Check generalizations
---------------------

If your application is dynamic enough, or complex enough, you may find that you
want to generalize your check logic based on a permissions model, or something
similar.  To accomplish this you can create your own custom ``MenuItem``
implementation with a ``check`` method.

This assumes you have a ``utils`` package.

``utils/menus.py``::

    from django.core.urlresolvers import resolve

    from simple_menu import MenuItem


    class ViewMenuItem(MenuItem):
        """Custom MenuItem that checks permissions based on the view associated
        with a URL"""

        def check(self, request):
             """Check permissions based on our view"""
             is_visible = True
             match = resolve(self.url)

             # do something with match, and possibly change is_visible...

             self.visible = is_visible


``reports/menus.py``::

     from utils.menus import ViewMenuItem

     from simple_menu import Menu, MenuItem

     from django.core.urlresolvers import reverse

     # Since we use ViewMenuItem here we do not need to define checks, instead
     # the check logic will change their visibility based on the permissions
     # attached to the views we reverse here.
     reports_children = (
          ViewMenuItem("Staff Only", reverse("reports.views.staff")),
          ViewMenuItem("Superuser Only", reverse("reports.views.superuser"))
     )

     Menu.add_item("main", MenuItem("Reports Index",
                                    reverse("reports.views.index"),
                                    children=reports_children))


.. _simple_menu __init__.py source file: https://github.com/jazzband/django-simple-menu/blob/master/simple_menu/__init__.py
.. _Bootstrap Navbar Component: https://getbootstrap.com/docs/5.1/components/navbar/
