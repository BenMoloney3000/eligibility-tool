from django.shortcuts import redirect
from django.test import override_settings
from django.urls import path
from django.views.generic import TemplateView

from ..mixin import TrailMixin


#
# Fake setup data for unit testing
#

NullView = TemplateView.as_view(template_name="null.html")

urlpatterns = [
    path("page1/", NullView, name="page1"),
    path("page2/", NullView, name="page2"),
    path("page3/", NullView, name="page3"),
]


# This has to be behind the trail mixin in the hierachy to mimic a view.
class FakeView:
    def dispatch(self, request, *args, **kwargs):
        return True


class FakeTrail(TrailMixin, FakeView):
    trail_initial = ["FakeView"]
    trail_session_id = "None"

    def get_url_from_class_name(self, name):
        return name.lower()

    def set_trail(self, trail):
        self.saved_trail = trail


#
# Actual tests
#


def test_get_prev_url_1():
    """If we're on page 3, then the last URL should be 2."""

    class Page3(FakeTrail):
        def get_trail(self):
            return ["Page1", "Page2", "Page3"]

    view = Page3()
    assert view.get_prev_url() == "page2"


def test_get_prev_url_2():
    """If we're on page Page1, then there should be no previous URL."""

    class Page1(FakeTrail):
        def get_trail(self):
            return ["Page1", "Page2", "Page3"]

    view = Page1()
    assert view.get_prev_url() is None


@override_settings(ROOT_URLCONF="prospector.trail.tests.test_trail")
def test_redirect():
    """Navigating to page 3 from page 2 should put page 3 in the trail."""

    class Page2(FakeTrail):
        def get_trail(self):
            return ["Page1", "Page2"]

    view = Page2()

    view.redirect("Page3")

    assert view.saved_trail == ["Page1", "Page2", "Page3"]


@override_settings(ROOT_URLCONF="prospector.trail.tests.test_trail")
def test_allowed_view():
    """Navigating to Page2 should be allowed if it's in the trail."""

    class Page2(FakeTrail):
        def get_trail(self):
            return ["Page1", "Page2"]

    view = Page2()

    assert view.dispatch(None) is True


@override_settings(ROOT_URLCONF="prospector.trail.tests.test_trail")
def test_disallowed_view():
    """Navigating to Page3 should redirect to Page2 if Page3 is not in the trail."""

    class Page3(FakeTrail):
        def get_trail(self):
            return ["Page1", "Page2"]

    view = Page3()

    assert view.dispatch(None).url == redirect("page2").url
