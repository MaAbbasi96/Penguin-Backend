from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from Polling.models import User
from Polling.services import PollingServices


class PollManagementViewTest(APITestCase):
    def setUp(self):
        User.objects.create(username='test_user', email='email@example.com')

    @mock.patch.object(PollingServices, 'create_poll')
    def test_create_poll(self, mocked_create_poll):
        response = self.client.post(reverse('create-poll'), {
            'username': 'test_user',
            'title': 'title',
            'description': 'description',
            'options': [
                'option1',
                'option2'
            ],
            'participants': [
                'user1',
                'user2'
            ]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'User does not exist')
        mocked_create_poll.assert_called_once_with('title', 'description', User.objects.get(username='test_user'),
                                                   ['option1', 'option2'], ['user1', 'user2'])
