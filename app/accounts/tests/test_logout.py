from html.parser import HTMLParser

from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.contrib.auth.views import LogoutView
from django.contrib.sessions.backends.signed_cookies import SessionStore
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.urls import reverse


def logout_request(method, *, csrf=False):
    factory = RequestFactory()
    path = reverse("accounts:logout")
    if csrf:
        token_request = factory.get(path)
        token = get_token(token_request)
        factory.cookies[settings.CSRF_COOKIE_NAME] = token_request.META["CSRF_COOKIE"]
        request = factory.post(path, {"csrfmiddlewaretoken": token})
    else:
        request = getattr(factory, method)(path)
    request.user = get_user_model()(pk=1, email="logout@example.com")
    request.session = SessionStore()
    request.session[SESSION_KEY] = "1"
    return request


def test_logout_post_clears_session_and_user():
    request = logout_request("post", csrf=True)

    response = LogoutView.as_view()(request)

    assert response.status_code == 200
    assert SESSION_KEY not in request.session
    assert not request.user.is_authenticated


def test_logout_get_is_rejected_without_clearing_session():
    request = logout_request("get")

    response = LogoutView.as_view()(request)

    assert response.status_code == 405
    assert request.session[SESSION_KEY] == "1"
    assert request.user.is_authenticated


def test_logout_post_requires_csrf_token():
    request = logout_request("post")

    response = LogoutView.as_view()(request)

    assert response.status_code == 403
    assert request.session[SESSION_KEY] == "1"
    assert request.user.is_authenticated


class LogoutFormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_logout_form = False
        self.has_csrf_token = False
        self.has_submit_button = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form":
            self.in_logout_form = (
                attrs.get("action") == reverse("accounts:logout")
                and attrs.get("method") == "post"
            )
        if self.in_logout_form:
            if tag == "input" and attrs.get("name") == "csrfmiddlewaretoken":
                self.has_csrf_token = bool(attrs.get("value"))
            if tag == "button" and attrs.get("type") == "submit":
                self.has_submit_button = True

    def handle_endtag(self, tag):
        if tag == "form":
            self.in_logout_form = False


def test_navigation_renders_logout_post_form_with_csrf():
    request = logout_request("get")
    parser = LogoutFormParser()

    parser.feed(render_to_string("base.html", request=request))

    assert parser.has_csrf_token
    assert parser.has_submit_button
