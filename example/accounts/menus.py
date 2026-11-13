from django.urls import reverse

from simple_menu import Menu, MenuItem


def profile_title(request):
    """Return a personalized title for our profile menu item
    """
    # we don't need to check if the user is authenticated because our menu
    # item will have a check that does that for us
    name = request.user.get_full_name() or request.user

    return f"{name}'s Profile"


submenu_items = [
    MenuItem(f"Page {i}",
             reverse('accounts:subpage', kwargs={'i': i}),
             icon=f'{i}-circle')
    for i in range(1, 4)
]

# Test sub menu with space
submenu_items.append(MenuItem(f"Page with space", reverse('accounts:space_test')))

Menu.add_item("user", MenuItem("Subpages",
                               reverse('accounts:subpage', kwargs={'i': 1}),
                               icon="menu-app",
                               children=submenu_items))

# this item will be shown to users who are not logged in
Menu.add_item("user", MenuItem("Sign in",
                               reverse('accounts:sign_in'),
                               icon='box-arrow-in-right',
                               check=lambda r: not r.user.is_authenticated))

# this will only be shown to logged in users and also demonstrates how to use
# a callable for the title to return a customized title for each request
Menu.add_item("user", MenuItem(profile_title,
                               reverse('accounts:profile'),
                               icon='person-circle',
                               check=lambda r: r.user.is_authenticated))

# this only shows to superusers
Menu.add_item("user", MenuItem("Secret superuser page",
                               reverse("accounts:super_only"),
                               icon='incognito',
                               check=lambda r: r.user.is_superuser))

Menu.add_item("user", MenuItem("Sign out",
                               reverse('accounts:sign_out'),
                               icon='box-arrow-right',
                               check=lambda r: r.user.is_authenticated))
