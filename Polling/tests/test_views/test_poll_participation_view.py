from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from Polling.enums import OptionStatus, PollStatus
from Polling.models import User, Poll, PollOption, UserPoll


class PollManagementParticipationViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user', email='email@example.com')
        self.participated_user = User.objects.create(username='p_user', email='email2@example.com')
        self.poll = Poll.objects.create(title='title', description='description', owner=self.user)
        self.user_poll = UserPoll.objects.create(poll=self.poll, user=self.participated_user,
                                                 choices={'option1': OptionStatus.NO.value})
        self.poll_option = PollOption.objects.create(poll=self.poll, value='option1', final=False)

    def test_get_participated_polls_user_exists(self):
        response = self.client.get(reverse('get-participated-polls'), {
            'username': 'p_user',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'User does not exist')
        obj = {
            'id': self.poll.id,
            'title': 'title',
            'description': 'description',
            'final_option': None,
            'options': {
                'option1': {'maybe': 0, 'yes': 0}
            },
            'status': 0,
            'creator': self.user.username
        }
        self.assertDictEqual(dict(response.data[0]), obj)

    def test_get_participated_polls_user_doesnt_exist(self):
        response = self.client.get(reverse('get-created-polls'), {
            'username': 'fake_user',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'User does not exist')


    def test_get_poll_user_and_poll_exists(self):
        response = self.client.get(reverse('get-poll', kwargs={'poll_id': self.poll.id}), {
            'username': 'test_user',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'User does not exist')
        obj = {
            'id': self.poll.id,
            'title': 'title',
            'description': 'description',
            'final_option': None,
            'options': {
                'option1': {'maybe': 0, 'yes': 0}
            },
            'status': 0,
            'creator': self.user.username
        }
        self.assertDictEqual(response.data, obj)

    def test_get_poll_user_does_not_exist(self):
        response = self.client.get(reverse('get-poll', kwargs={'poll_id': self.poll.id}), {
            'username': 'fake_user',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'User does not exist')

    def test_get_poll_poll_does_not_exist(self):
        response = self.client.get(reverse('get-poll', kwargs={'poll_id': self.poll.id + 10}), {
            'username': 'test_user',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'Poll does not exist')

    def test_vote_user_and_poll_exists(self):
        response = self.client.post(reverse('vote', kwargs={'poll_id': self.poll.id}), {
            'username': 'p_user',
            'options': {
                'option1': 1,
            }
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'User has no access to this poll')
        self.assertEqual(UserPoll.objects.get(id=self.user_poll.id).choices['option1'], 1)

    def test_vote_user_doesnt_exist(self):
        response = self.client.post(reverse('vote', kwargs={'poll_id': self.poll.id}), {
            'username': 'fake_user',
            'options': {
                'option1': 1,
            }
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'User does not exist')

    def test_vote_poll_doesnt_exist(self):
        response = self.client.post(reverse('vote', kwargs={'poll_id': self.poll.id + 10}), {
            'username': 'p_user',
            'options': {
                'option1': 1,
            }
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'Poll does not exist')

    def test_vote_user_has_no_access(self):
        response = self.client.post(reverse('vote', kwargs={'poll_id': self.poll.id}), {
            'username': 'test_user',
            'options': {
                'option1': 1,
            }
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'User has no access to this poll')

    def test_vote_for_closed_poll(self):
        self.poll.status = PollStatus.CLOSED.value
        self.poll.save()
        response = self.client.post(reverse('vote', kwargs={'poll_id': self.poll.id}), {
            'username': 'p_user',
            'options': {
                'option1': 1,
            }
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT, 'Poll is closed and cannot vote for it')
