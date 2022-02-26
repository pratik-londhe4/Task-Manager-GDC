import json
from datetime import datetime
from io import StringIO
from unittest.mock import patch
from urllib import request

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .models import History, Report, Task
from .tasks import send_email_report
from .views import (GenereicAllTaskView, GenereicCompletedTaskView,
                    GenereicPendingTaskView, GenericTaskUpdateView, GenericTaskDeleteView, GenericTaskCreateView)


class QuestionModelTests(TestCase):
    def setUp(self):

        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="bruce_wayne", email="bruce@wayne.org", password="i_am_batman")

        self.client.login(username="bruce_wayne", password="i_am_batman")

    def test_authenticated(self):
        request = self.factory.get("/tasks")
        request.user = self.user
        response = GenereicAllTaskView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        request.user = AnonymousUser()
        response = GenericTaskUpdateView.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_completed_task_view(self):
        task = Task(title="Completed task test", description="des",
                    priority=5, user=self.user, completed=True)
        task.save()

        request = self.factory.get("/tasks/completed")
        request.user = self.user
        response = GenereicCompletedTaskView.as_view()(request)
        response.render()
        self.assertInHTML(task.title, response.content.decode())

    def test_pending_task_view(self):
        task = Task(title="pending task test", description="des",
                    priority=5, user=self.user)
        task.save()

        request = self.factory.get("/tasks")
        request.user = self.user
        response = GenereicPendingTaskView.as_view()(request)
        response.render()
        self.assertInHTML(task.title, response.content.decode())

    def test_delete_task_view(self):
        task = Task(title="delete task test", description="des",
                    priority=5, user=self.user)
        task.save()

        request = self.factory.get("/tasks/delete")
        request.user = self.user
        response = GenericTaskDeleteView.as_view()(request, pk=1)
        self.assertNotIn(task.title, Task.objects.filter(user=self.user))

    def test_create_task(self):
        self.client.post(
            '/tasks/create/', {'title': 'test task', 'description': 'description', 'priority': 5, 'user': self.user})

        self.assertEqual(Task.objects.last().title, "TEST TASK")

    def test_task_cascade(self):
        task1 = {'title': "cascade", 'description': "des",
                 'priority': 5, 'user': self.user}
        task2 = {'title': "cascade task test 2", 'description': "des",
                 'priority': 5, 'user': self.user}

        request = self.factory.post('/tasks/create', data=task1)
        request.user = self.user
        GenericTaskCreateView.as_view()(request)
        request = self.factory.post('/tasks/create', data=task1)
        request.user = self.user
        GenericTaskCreateView.as_view()(request)

        self.assertEqual(Task.objects.get(id=1).priority, 6)

    def test_history(self):
        task = Task(title="history test", description="des",
                    priority=5, user=self.user)

        task.save()
        task.status = 'C'
        task.save()

        self.assertEqual(History.objects.last().new_status, 'C')

    def test_api_tasks(self):
        task = Task(title="api get test", description="des",
                    priority=5, user=self.user).save()

        tasks = self.client.get('/api/tasks/')
        self.assertTrue("api get test" in json.loads(
            tasks.content)[0].values())

    def test_email_report(self):
        report = Report(reminder_time=datetime.now().strftime(
            '%H:%M'), user=self.user, disabled=False)

        report.save()
        send_email_report()
        with patch('sys.stdout', new=StringIO()) as out:
            self.assertIn(out.getvalue(), "bruce@wayne.org")
