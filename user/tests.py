from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.contrib.auth.models import AnonymousUser
from .views import UserCreateView, UserLoginView


class QuestionModelTests(TestCase):
    def setUp(self):

        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="bruce_wayne", email="bruce@wayne.org", password="i_am_batman")

    def test_signup(self):
        request = self.factory.get("/user/signup")
        request.user = self.user
        response = UserCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        request = self.factory.get("/user/login")
        request.user = self.user
        response = UserLoginView.as_view()(request)
        self.assertEqual(response.status_code, 200)
