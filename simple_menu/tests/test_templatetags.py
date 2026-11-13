from rich.pretty import pprint as rpprint

from django.template import Context
from django.template import Template
from django.test import RequestFactory
from django.test import SimpleTestCase

from simple_menu import Menu
from simple_menu import MenuItem


def pprint(context: Context):
    return rpprint(context.flatten())


class TemplateTagTests(SimpleTestCase):
    request_factory = RequestFactory()
    template = Template("{% load simple_menu %}{% generate_menu %}")

    def setUp(self):
        grandchildren = [
            MenuItem("Grandchild 1", "/parent/child1/grandchild1"),
            MenuItem("Grandchild 2", "/parent/child1/grandchild2"),
        ]

        children = [
            MenuItem("Child 1", "/parent/child1", children=grandchildren),
            MenuItem("Child 2", "/parent/child2"),
        ]

        Menu.add_item(
            "test",
            MenuItem("Parent", "/parent", children=children),
        )
        Menu.add_item("test", MenuItem("Sibling", "/sibling"))

        Menu.add_item("test2", MenuItem("Other menu", "/other"))

    def tearDown(self):
        Menu.items = {}
        Menu.sorted = {}
        Menu.loaded = False

    def test_generate_menu_finds_menus(self):
        request = self.request_factory.get("/")
        context = Context({"request": request})
        self.template.render(context)

        menus = context.get("menus")

        self.assertIsInstance(menus, dict)
        self.assertIn("test", menus)
        self.assertIsInstance(menus["test"], list)

    def test_generate_menu_matches_parent(self):
        request = self.request_factory.get("/parent")
        context = Context({"request": request})
        self.template.render(context)

        selected_menu = context.get("selected_menu")

        self.assertIsInstance(selected_menu, MenuItem)
        self.assertEqual(selected_menu.url, "/parent")

    def test_generate_menu_matches_child(self):
        request = self.request_factory.get("/parent/child1")
        context = Context({"request": request})
        self.template.render(context)

        pprint(context)

        self.assertTrue(context.get("has_submenu"))
        selected_submenu = context.get("submenu")

        self.assertIsInstance(selected_submenu, list)
        # self.assertIsInstance(selected_submenu[0], MenuItem)
        # self.assertEqual(selected_submenu[0].url, "/parent/child1")

    def test_generate_menu_matches_child2(self):
        request = self.request_factory.get("/parent/child2")
        context = Context({"request": request})
        self.template.render(context)

        pprint(context)

        self.assertTrue(context.get("has_submenu"))
        selected_submenu = context.get("submenu")

        self.assertIsInstance(selected_submenu, list)
        # self.assertIsInstance(selected_submenu[0], MenuItem)
        # self.assertEqual(selected_submenu[0].url, "/parent/child2")

    def test_generate_menu_matches_grandchild(self):
        request = self.request_factory.get("/parent/child1/grandchild1")
        context = Context({"request": request})
        self.template.render(context)

        pprint(context)

        self.assertTrue(context.get("has_submenu"))
        # selected_submenu = context.get("submenu")

        # self.assertIsInstance(selected_submenu, list)
        # self.assertIsInstance(selected_submenu[0], MenuItem)
        # self.assertEqual(selected_submenu[0].url, "/parent/child1/grandchild1")

    def test_generate_menu_doesnt_match_invalid_item(self):
        request = self.request_factory.get("/unrelated")
        context = Context({"request": request})
        self.template.render(context)

        self.assertIsNone(context.get("selected_menu"))

    def test_generate_menu_renders_nothing(self):
        request = self.request_factory.get("/")
        out = self.template.render(Context({"request": request}))

        self.assertHTMLEqual(out, "")

    def test_generate_menu_renders_error_without_request(self):
        out = self.template.render(Context())

        self.assertIn("menu failed to render", out)
        self.assertHTMLEqual(out, "")
