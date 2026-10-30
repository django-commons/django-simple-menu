from django import template
from .. import Menu

register = template.Library()

class MenuNode(template.Node):
    def __init__(self):
        pass

    def render(self, context):
        # if a 500 error happens we get an empty context, in which case
        # we should just return to let the 500.html template render
        if 'request' not in context:
            return '<!-- menu failed to render due to missing request in the context -->'

        menus = Menu.process(context['request'])

        # recursively find the selected item
        def find_selected(menu):
            process = []
            for item in menu:
                if item.selected:
                    return item
                if len(item.children) > 0:
                    process.append(item)
            for item in process:
                r = find_selected(item.children)
                if r is not None:
                    return r
            return None

        # Making it backward compatible (these should probably be renamed selected_menuitem and selected_menu, respectively)
        selected_menu = None
        selected_menu_menu = None
        for name in menus:
            found_menu = find_selected(menus[name])
            if found_menu:
                if selected_menu is None or len(selected_menu.url) < len(found_menu.url):
                    # since our call to Menu.process above allows for menus
                    # in multiple menus we reset the selected attr to False
                    # if we find a more specific match
                    if selected_menu is not None:
                        selected_menu.selected = False

                    selected_menu = found_menu
                    selected_menu_menu = menus[name]

        # now for the submenu
        submenu = []
        has_submenu = False
        if selected_menu is not None:
            if selected_menu.parent is not None:
                submenu = selected_menu.parent.children
                has_submenu = True
            elif len(selected_menu.children) > 0:
                submenu = selected_menu.children
                has_submenu = True

        # set the items in our context
        context['menus'] = menus
        context['selected_menu'] = selected_menu
        context['selected_menu_menu'] = selected_menu_menu
        context['submenu'] = submenu
        context['has_submenu'] = has_submenu

        return ''

def generate_menu(parser, token):
    return MenuNode()
register.tag('generate_menu', generate_menu)
