from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.contrib.auth.models import AnonymousUser
from .views import GenereicAllTaskView


class QuestionModelTests(TestCase):
    def setUp(self):

        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="bruce_wayne", email="bruce@wayne.org", password="i_am_batman")

    def test_authenticated(self):
        # Create an instance of a GET request.
        request = self.factory.get("/tasks")
        # Set the user instance on the request.
        request.user = self.user
        # We simply create the view and call it like a regular function
        response = GenereicAllTaskView.as_view()(request)
        # Since we are authenticated we get a 200 response
        self.assertEqual(response.status_code, 200)
