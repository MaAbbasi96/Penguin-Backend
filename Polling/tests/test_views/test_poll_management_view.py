from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from Polling.enums import PollStatus
from Polling.models import User, Poll, NormalPollOption
from Polling.services import PollingServices


class PollManagementViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user', email='email@example.com')
        self.user1 = User.objects.create(username='user1', email='email1@example.com')
        self.user2 = User.objects.create(username='user2', email='email2@example.com')
        self.poll = Poll.objects.create(title='title', description='description', owner=self.user)
        self.poll_option = NormalPollOption.objects.create(poll=self.poll, value='option1', final=False)

    @mock.patch.object(PollingServices, 'create_poll')
    def test_create_poll_user_exists(self, mocked_create_poll):
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
            ],
            'is_normal': True,
            'message': 'salam'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'User does not exist')
        mocked_create_poll.assert_called_once_with('title', 'description', User.objects.get(username='test_user'),
                                                   ['option1', 'option2'], ['user1', 'user2'], True, 'salam')

    @mock.patch.object(PollingServices, 'create_poll')
    def test_create_poll_user_doesnt_exist(self, mocked_create_poll):
        response = self.client.post(reverse('create-poll'), {
            'username': 'fake_username',
            'title': 'title',
            'description': 'description',
            'options': [
                'option1',
                'option2'
            ],
            'participants': [
                'user1',
                'user2'
            ],
            'is_normal': True,
            'message': 'salam'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'User does not exist')
        mocked_create_poll.assert_not_called()

    @mock.patch.object(PollingServices, 'edit_poll')
    def test_edit_poll_happy_path(self, mocked_edit_poll):
        self.poll_option.final = True
        self.poll.status = PollStatus.CLOSED.value
        response = self.client.put(reverse('edit-poll', kwargs={'poll_id': self.poll.id}), {
            'username': 'test_user',
            'message': 'message'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'User does not exist')
        mocked_edit_poll.assert_called_once_with(self.poll, 'message')

    def test_edit_poll_poll_is_not_final(self):
        response = self.client.put(reverse('edit-poll', kwargs={'poll_id': self.poll.id}), {
            'username': 'test_user',
            'message': 'message'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT, 'Poll is not final')

    def test_get_created_polls_user_exists(self):
        response = self.client.get(reverse('get-created-polls'), {
            'username': 'test_user',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'User does not exist')
        obj = {
            'id': self.poll.id,
            'title': 'title',
            'description': 'description',
            'final_option': None,
            'options': {
                str(self.poll_option.id): {'maybe': 0, 'yes': 0, 'value': 'option1'}
            },
            'status': 0,
            'creator': self.user.username,
            'is_normal': True,
        }
        self.assertDictEqual(dict(response.data[0]), obj)

    def test_get_created_polls_user_doesnt_exist(self):
        response = self.client.get(reverse('get-created-polls'), {
            'username': 'fake_user',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'User does not exist')

    @mock.patch.object(PollingServices, 'finalize_poll')
    def test_finalize_user_exists(self, mocked_finalize_poll):
        response = self.client.post(reverse('finalize-poll', kwargs={'poll_id': self.poll.id}), {
            'username': 'test_user',
            'option': str(self.poll_option.id)
        }, format='json')
        # print(Poll.objects.get(id=self.poll.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'user or poll does not exist')
        mocked_finalize_poll.assert_called_once_with(self.poll, self.poll_option)

    @mock.patch.object(PollingServices, 'finalize_poll')
    def test_finalize_user_doesnt_exist(self, mocked_finalize_poll):
        response = self.client.post(reverse('finalize-poll', kwargs={'poll_id': self.poll.id}), {
            'username': 'fake_user',
            'option': 'option1'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'User does not exist')
        mocked_finalize_poll.assert_not_called()

    @mock.patch.object(PollingServices, 'finalize_poll')
    def test_finalize_poll_doesnt_exist(self, mocked_finalize_poll):
        response = self.client.post(reverse('finalize-poll', kwargs={'poll_id': self.poll.id + 10}), {
            'username': 'test_user',
            'option': 'option1'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'Poll does not exist')
        mocked_finalize_poll.assert_not_called()
