import signal
import threading
from queue import Queue

from django.conf import settings
from django.template import Template, Context
from django.test import TestCase, override_settings
from django.test.client import RequestFactory

from simple_menu import Menu, MenuItem

# XXX TODO: test MENU_HIDE_EMPTY


class CustomMenuItem(MenuItem):
    """
    Custom MenuItem subclass with custom check logic
    """
    def check(self, request):
        """
        We should be visible unless the request path ends with "foo"
        """
        self.visible = not request.path.endswith("foo")


class MenuTests(TestCase):
    """
    Tests for Menu
    """

    def setUp(self):
        """
        Build some menus for our tests
        """
        self.kids3_2_desired_title = None
        def kids3_2_title(request):
            "Allow the title of kids3-2 to be changed"
            if self.kids3_2_desired_title is not None:
                return "-".join([request.path, self.kids3_2_desired_title])
            return 'kids3-2'

        self.kids3_2_desired_url = None
        def kids3_2_url(request):
            "Allow the url of kids3-2 to be changed"
            if self.kids3_2_desired_url is not None:
                return '/'.join([request.path, self.kids3_2_desired_url])
            return '/parent3/kids3-2'

        def kids2_2_check(request):
            "Hide kids2-2 whenever the request path ends with /hidden"
            if request.path.endswith('/hidden'):
                return False
            return True

        # Ensure we can pass children as tuples (or other iterables, like generators)
        # Following the implementation of sorted children there was a bug reported due to children
        # being passed as a tuple, which has no .sort method
        # See: https://github.com/jazzband/django-simple-menu/issues/38
        def kids2():
            "Generator for kids2"
            class RepeatIterator:
                "We need this to be reusable -- http://stackoverflow.com/a/1985733"
                def __iter__(self):
                    yield MenuItem("kids2-1", "/parent2/kids2-1", weight=999)
                    yield MenuItem("kids2-2", "/kids2-2", check=kids2_2_check)
            return RepeatIterator()

        def kids3_1(request):
            "Callable for kids3-1"
            return [
                MenuItem("kids3-1-1", "/parent3/kids3-1/kid1", exact_url=True),
            ]

        kids3 = (
            CustomMenuItem("kids3-1", "/parent3/kids3-1", children=kids3_1, slug="salty"),
            CustomMenuItem(kids3_2_title, kids3_2_url)
        )

        Menu.items = {}
        Menu.sorted = {}
        Menu.loaded = False

        # add our items.  because we set weight to 999 for parent 1 it will become the last child
        # even though it's added first
        Menu.add_item("test", MenuItem("Parent 1", "/parent1", weight=999))
        Menu.add_item("test", MenuItem("Parent 2", "/parent2", children=kids2()))
        Menu.add_item("test", MenuItem("Parent 3", "/parent3", children=kids3))

        self.factory = RequestFactory()

    def test_custom_menuitem(self):
        """
        Ensure our custom check on our custom MenuItem works
        """
        request = self.factory.get('/parent3/kids3-1')
        items = Menu.process(request, 'test')
        self.assertEqual(len(items[1].children), 2)

        request = self.factory.get('/parent3/kids3-1/foo')
        items = Menu.process(request, 'test')
        self.assertEqual(len(items[1].children), 0)

    def test_thread_safety_and_checks(self):
        """
        Ensure our thread safety works, this also ensures our checks work
        """
        # this shouldn't ever take more than 5 seconds, add a safety in case someting breaks
        signal.alarm(5)

        def t1(results):
            "Closure for thread 1"
            request = self.factory.get('/kids2-2/visible')
            items = Menu.process(request, 'test')
            results.put_nowait(len(items[0].children) == 2)

        def t2(results):
            "Closure for thread 2"
            request = self.factory.get('/kids2-2/hidden')
            items = Menu.process(request, 'test')
            results.put_nowait(len(items[0].children) == 1)

        results = Queue()
        for _ in range(50):
            threads = [
                threading.Thread(target=t1, args=(results,)),
                threading.Thread(target=t2, args=(results,))
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()


        self.assertTrue(all([
            results.get()
            for _ in range(100)
        ]))

    def test_slug(self):
        """
        Ensure our slugification works as expected
        """
        request = self.factory.get('/parent3/kids3-1')
        items = Menu.process(request, 'test')
        self.assertEqual(items[1].slug, "parent-3")
        self.assertEqual(items[1].children[0].slug, "salty")

    def test_exact_url(self):
        """
        Ensure that the exact_url setting works
        """
        # the extra stuff will still cause kids3-2 to be selected
        request = self.factory.get('/parent3/kids3-2/extra_stuff_here')
        items = Menu.process(request, 'test')
        self.assertEqual(items[1].children[1].selected, True)

        # but here it won't, because exact_url is set
        request = self.factory.get('/parent3/kids3-1/kid1/extra_stuff_here')
        items = Menu.process(request, 'test')
        self.assertEqual(items[1].children[0].children[0].selected, False)

    def test_callable_title(self):
        """
        Ensure callable titles work
        """
        self.kids3_2_desired_title = "fun"
        request = self.factory.get('/parent3')
        items = Menu.process(request, 'test')
        self.assertEqual(items[1].children[1].title, "/parent3-fun")

    def test_callable_url(self):
        """
        Ensure callable urls work
        """
        self.kids3_2_desired_url = "custom"
        request = self.factory.get('/parent3')
        items = Menu.process(request, 'test')
        self.assertEqual(items[1].children[1].url, "/parent3/custom")

    def test_select_parents(self):
        """
        Ensure the MENU_SELECT_PARENTS setting works
        """
        settings.MENU_SELECT_PARENTS = False
        request = self.factory.get('/parent2/kids2-1')
        items = Menu.process(request, 'test')
        self.assertEqual(items[0].selected, True)
        self.assertEqual(items[0].children[1].selected, True)
        self.assertEqual(items[1].selected, False)

        request = self.factory.get('/kids2-2')
        items = Menu.process(request, 'test')
        self.assertEqual(items[0].selected, False)
        self.assertEqual(items[0].children[0].selected, True)
        self.assertEqual(items[1].selected, False)

        settings.MENU_SELECT_PARENTS = True
        request = self.factory.get('/kids2-2')
        items = Menu.process(request, 'test')
        self.assertEqual(items[0].selected, True)
        self.assertEqual(items[0].children[0].selected, True)
        self.assertEqual(items[1].selected, False)

        request = self.factory.get('/parent3/kids3-1/kid1')
        items = Menu.process(request, 'test')
        self.assertEqual(items[0].selected, False)
        self.assertEqual(items[0].children[1].selected, False)
        self.assertEqual(items[1].selected, True)
        self.assertEqual(items[1].children[0].selected, True)
        self.assertEqual(items[1].children[0].children[0].selected, True)
        self.assertEqual(items[1].children[1].selected, False)
        self.assertEqual(items[2].selected, False)

    def test_template_tag(self):
        """
        Ensure the templating works
        """
        request = self.factory.get('/parent3/kids3-1')
        out = Template(
            "{% load simple_menu %}"
            "{% generate_menu %}"
            "{% for item in menus.test %}"
            "{{ item.title }},"
            "{% for child in item.children %}"
            "{{ child.title }},"
            "{% for grandchild in child.children %}"
            "{{ grandchild.title }},"
            "{% endfor %}"
            "{% endfor %}"
            "{% endfor %}"
        ).render(Context({
            'request': request,
        }))

        self.assertEqual(out, "Parent 2,kids2-2,kids2-1,Parent 3,kids3-1,kids3-1-1,kids3-2,Parent 1,")

    def test_template_tag_missing_attribute(self):
        """
        Missing attributes should not raise exceptions in templates
        """
        request = self.factory.get('/parent2/kids2-1')
        out = Template(
            "{% load simple_menu %}"
            "{% generate_menu %}"
            "{% for item in menus.test %}"
            "{{ item.title }}{{ item.doesntexist }},"
            "{% endfor %}"
        ).render(Context({
            'request': request,
        }))

        self.assertEqual(out, "Parent 2,Parent 3,Parent 1,")

class MenuItemTests(TestCase):
    """
    Tests for MenuItem
    """

    def test_kwargs(self):
        """
        MenuItems should accept arbitrary keyword args
        """
        item = MenuItem("test", "/test", arbitrary=True, dictionary={'a': 1})
        self.assertTrue(item.arbitrary)
        self.assertEqual(item.dictionary, {'a': 1})
        self.assertRaises(AttributeError, lambda: item.nope)

    @override_settings(MENU_TRIM_NON_VISIBLE_CHILD_ITEMS=False)
    def test_trim_non_visible_child_items__disabled(self):
        """
        Ensure that non-visible child items are NOT trimmed from the menu
        """
        # Generate the menu
        child_item = MenuItem("child", "/child", visible=False)
        item = MenuItem("test", "/test", children=[child_item])

        # Process the item
        request = RequestFactory().get('/test')
        item.process(request)

        # Check that non-visible child items are still in the menu
        self.assertIn(child_item, item.children)

    def test_trim_non_visible_child_items__enabled(self):
        """
        Ensure that non-visible child items are trimmed from the menu.

        This is the default behaviour
        """
        # Generate the menu
        child_item = MenuItem("child", "/child", visible=False)
        item = MenuItem("test", "/test", children=[child_item])

        # Process the item
        request = RequestFactory().get('/test')
        item.process(request)

        # Check that non-visible child items removed still in the menu
        self.assertNotIn(child_item, item.children)
