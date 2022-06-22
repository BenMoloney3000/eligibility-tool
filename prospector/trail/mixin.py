from typing import List
from typing import Optional
from urllib.parse import urlencode

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import reverse


def snake_case(name: str, separator: str):
    """
    Turn NamesLikeThis into names_like_this.

    e.g. pass in "NumOccupants" and it'll produce "num_occupants"

    separator gives the character to put between words, e.g. snake-case, or snake_case.
    """
    # https://stackoverflow.com/a/44969381/10956063
    return "".join([separator + c.lower() if c.isupper() else c for c in name]).lstrip(
        separator
    )


class TrailMixin:
    """
    Keep a breadcrumb trail of the user's progress.

    This mixin provides a trail of where the user has been.  It's designed for
    multi-stage forms.  It allows the user to go back to pages previously visited,
    but not to go forwards to pages they haven't.

    A worked-through example
    ========================

    The trail starts off containing the first page.  We're going to be starting at
    Assets1, so:

    trail = [ "Assets1" ]

    The user requests Assets1 (GET).  This is in the trail, so everything is good.

    Now the user POSTs the form.  It's valid!  So we're going to go to Assets2.  To
    do this, we first add it to the trail:

    trail = [ "Assets1", "Assets2" ]

    And then we redirect.  So the browser fetches Assets2 (GET).  Again, it's in
    the trail, so there's no problem.

    Assets2 is POSTED.  It's valid, so we move onto checking the address.  So add
    it to the trail:

    trial = [ "Assets1", "Assets2", "CheckAddress" ]

    And redirect.

    Now...

    The user tries to load "SmartMeters".  However, it's not in the trail.  So we
    just redirect to the most recent entry in the trail: CheckAddress.

    Now, the user navigates back and ends up on Assets2.  It's in the path, so that's
    fine, we serve the page.

    The trail is still: [ "Assets1", "Assets2", "CheckAddress" ] - it's not
    modified on GET, only POST.

    Now, the user posts the Assets2 form.  What happens now?

    The user has entered someting different from before and will now be set on
    a different path.  So we pare the trail so that it ends with the current
    view ("Assets2").  Because we're redirecting somewhere else, we add that
    to the end:

    trail = [ "Assets1", "Assets2" ] + [ "Followup" ]

    Now the user hits back a couple of times and ends up GETting Assets1.  All
    good, it's in the trail:

    trail = [ "Assets1", "Assets2", "Followup" ]

    When assets1 is POSTed again, the trail will be pared down to finish at
    Assets1, and the redirect would re-add the next entry:

    trail = [ "Assets1" ] + [ "Assets2" ]

    This system means:
     1. Users can't produce invalid state by navigating to random pages
     2. Redirect logic is local to the view that does the redirecting
     3. The back button works

    How to use
    ==========

    1. Set trail_initial to a list containing one entry which is the stringified version
       of the class name

    2. Set the trail_session_id to smoething unique

    3. Use self.redirect() to move to the next page.

    4. Set trail_url_prefix to the URL prefix for your app given in the urlconf.  So
       if you'd refer to views in your app like "member_signup:view-name", this should
       be "member_signup:".  Your class names and their URLconf names should follow the
       following convention:  a class called NameLikeThis should have the urlconf name
       "name-like-this".
    """

    trail_initial: List[str]
    trail_session_id: str
    trail_url_prefix: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if len(self.trail_initial) < 1:
            raise ImproperlyConfigured(
                "ViewTrailMixin subclass must have at least one element in its initial trail"
            )

        if not self.trail_session_id:
            raise ImproperlyConfigured(
                "ViewTrailMixin subclass must set trail_session_id so it can find data in the request session"
            )

    def set_trail(self, trail):
        # This is just for mocking, really.
        self.request.session[self.trail_session_id] = trail

    def get_trail_initial(self):
        """Get the starting page for the trail."""
        return self.trail_initial

    def get_trail(self):
        if self.trail_session_id in self.request.session:
            return self.request.session[self.trail_session_id]
        else:
            return self.get_trail_initial().copy()

    def get_view_name(self):
        return self.__class__.__name__

    def prereq(self) -> Optional[HttpResponse]:
        """Override to perform check(s) before displaying the page."""
        return None

    def get_url_from_class_name(self, class_name):
        """
        Turn a class name into something we can give to Django's `reverse` function.

        e.g. "ClassName" -> "app-name:class-name"
        """
        url = snake_case(class_name, separator="-")
        return self.trail_url_prefix + url

    def _check_trail(self):
        trail = self.get_trail()
        if self.get_view_name() not in trail:
            # Redirect to the last thing in the trail
            return redirect(self.get_url_from_class_name(trail[-1:][0]))
        else:
            return None

    def dispatch(self, request, *args, **kwargs):
        """Check whether anything prevents us seeing this page."""

        # Like it not being in the trail
        trail_check_action = self._check_trail()

        if trail_check_action:
            return trail_check_action

        else:
            # Or not meeting the prerequisites
            prereq_action = self.prereq()

            if prereq_action:
                return prereq_action
            else:
                # Looks like we can see the page.
                return super().dispatch(request, *args, **kwargs)

    def redirect(self, next_view: str = None, query: str = None):
        """
        Redirect to the next view, adding it to the trail.

        If next_view is not supplied, get_next() is called.
        """

        trail = self.get_trail()
        this_view = self.get_view_name()

        if not next_view:
            next_view = self.get_next()

        assert this_view in trail

        # We're going to redirect, so we start the trail at the current view, even
        # if the user previously navigated further.
        cutoff = trail.index(this_view) + 1

        self.set_trail([*trail[0:cutoff], next_view])

        url = reverse(self.get_url_from_class_name(next_view))
        if query:
            url += "?" + urlencode(query)
        return HttpResponseRedirect(url)

    def get_next(self):
        """
        Return the name of the next class to navigate to.

        Note this is the class name as a string, e.g "LovesClubbingSeals", and not a
        reference to the class itself.

        Override this to get dynamic redirection behaviour.
        """
        return self.next

    def get_percent_complete(self) -> int:
        return 0

    def get_prev_url(self) -> Optional[str]:
        trail = self.get_trail()
        this_view = trail.index(self.get_view_name())
        if this_view > 0:
            last = trail[:this_view][-1]
            return self.get_url_from_class_name(last)
        else:
            return None
