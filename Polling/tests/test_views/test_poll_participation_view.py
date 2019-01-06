from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from Polling.enums import OptionStatus, PollStatus
from Polling.models import User, Poll, NormalPollOption, UserPoll, Comment


class PollParticipationViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user', email='email@example.com')
        self.participated_user = User.objects.create(username='p_user', email='email2@example.com')
        self.poll = Poll.objects.create(title='title', description='description', owner=self.user)
        self.poll_option = NormalPollOption.objects.create(poll=self.poll, value='option1', final=False)
        self.user_poll = UserPoll.objects.create(poll=self.poll, user=self.participated_user,
                                                 choice={str(self.poll_option.id): OptionStatus.NO.value})
        self.comment = Comment.objects.create(user=self.participated_user, option=self.user_poll, parent=None,
                                              message='I am a comment!')

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
                str(self.poll_option.id): {'maybe': 0, 'yes': 0, 'value': 'option1'}
            },
            'status': 0,
            'creator': self.user.username,
            'is_normal': True
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
                str(self.poll_option.id): {'maybe': 0, 'yes': 0, 'value': 'option1'}
            },
            'status': 0,
            'creator': self.user.username,
            'is_normal': True
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
                str(self.poll_option.id): 1,
            }
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'User has no access to this poll')
        self.assertEqual(UserPoll.objects.get(id=self.user_poll.id).choice[str(self.poll_option.id)], 1)

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

    def test_vote_with_invalid_options(self):
        self.poll.status = PollStatus.CLOSED.value
        self.poll.save()
        response = self.client.post(reverse('vote', kwargs={'poll_id': self.poll.id}), {
            'username': 'p_user',
            'options': {
                'option1': True,
            }
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT, 'Option type is not in OptionStatus enum')

    def test_comment_happy_path(self):
        response = self.client.post(reverse('comment',
                                            kwargs={'poll_id': self.poll.id, 'option_id': self.user_poll.id}), {
            'username': 'p_user',
            'message': 'hi',
            'parent_id': 0
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'User has no access to this poll')
        self.assertEqual(Comment.objects.filter(user=self.participated_user).count(), 1)

    def test_comment_user_option_doesnt_exist(self):
        response = self.client.post(reverse('comment',
                                            kwargs={'poll_id': self.poll.id, 'option_id': self.user_poll.id + 10}), {
            'username': 'p_user',
            'message': 'hi',
            'parent_id': 0
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'Option does not exist')

    def test_comment_parent_doesnt_exist(self):
        response = self.client.post(reverse('comment',
                                            kwargs={'poll_id': self.poll.id, 'option_id': self.user_poll.id}), {
            'username': 'p_user',
            'message': 'hi',
            'parent_id': -1
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'Parent does not exist')

    def test_comment_user_has_no_access(self):
        response = self.client.post(reverse('comment',
                                            kwargs={'poll_id': self.poll.id, 'option_id': self.user_poll.id}), {
            'username': 'test_user',
            'message': 'hi',
            'parent_id': -1
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'User has no access to this poll')

    def test_get_comments_happy_path(self):
        response = self.client.get(reverse('get_comments',
                                           kwargs={'poll_id': self.poll.id, 'option_id': self.poll_option.id}), {
            'username': 'test_user',
        }, format='json')
        obj = {
            'id': self.comment.id,
            'message': self.comment.message,
            'date': self.comment.date.strftime('%Y-%m-%d'),
            'user': self.participated_user.username,
            'option_id': str(self.poll_option.id),
            'parent': None
        }
        self.assertEqual(dict(response.data[0]), obj)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'User has no access to this poll')

    def test_get_comments_user_doesnt_exist(self):
        response = self.client.get(reverse('get_comments',
                                           kwargs={'poll_id': self.poll.id, 'option_id': self.poll_option.id}), {
            'username': 'fake_user',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'User doesnt exist')

    def test_get_comments_option_doesnt_exist(self):
        response = self.client.get(reverse('get_comments',
                                           kwargs={'poll_id': self.poll.id, 'option_id': self.poll_option.id + 10}), {
            'username': 'p_user',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'Option doesnt exist')
