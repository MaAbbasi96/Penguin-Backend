from unittest import mock

from django.core.mail import EmailMultiAlternatives
from django.test import TestCase

from Polling.enums import PollStatus
from Polling.models import User, Poll, NormalPollOption, UserPoll
from Polling.services import PollingServices


@mock.patch.object(EmailMultiAlternatives, 'send')
@mock.patch.object(EmailMultiAlternatives, '__init__', return_value=None)
class PollingServicesTest(TestCase):
    def setUp(self):
        self.services = PollingServices()
        self.owner = User.objects.create(username='owner', email='owner@example.com')
        self.user1 = User.objects.create(username='user1', email='user1@example.com')
        self.user2 = User.objects.create(username='user2', email='user2@example.com')
        self.title = 'title'
        self.description = 'description'

    def test_create_normal_poll(self, mocked_init, mocked_send):
        self.assertEqual(0, Poll.objects.all().count())
        self.assertEqual(0, NormalPollOption.objects.all().count())
        self.assertEqual(0, UserPoll.objects.all().count())
        self.services.create_poll(self.title, self.description, self.owner, ['option1', 'option2'],
                                  [self.user1, self.user2, ], True)
        expected_subject = 'Invitation to title polling'
        expected_message = 'Please participate in the poll title using your panel!'
        mocked_init.assert_called_with(expected_subject, expected_message, 'info@penguin.com',
                                       ['user1@example.com', 'user2@example.com'], connection=mock.ANY)
        mocked_send.assert_called()
        self.assertEqual(1, Poll.objects.all().count())
        self.assertEqual(self.owner, Poll.objects.first().owner)
        self.assertEqual(2, NormalPollOption.objects.all().count())
        self.assertListEqual(['option1', 'option2'],
                             list(NormalPollOption.objects.all().values_list('value', flat=True)),
                             'We have two poll options with values option1 and option2')
        self.assertEqual(2, UserPoll.objects.all().count())

    def test_finalize_normal_poll(self, mocked_init, mocked_send):
        poll = Poll.objects.create(owner=self.owner, title=self.title, description=self.description)
        option1 = NormalPollOption.objects.create(poll=poll, value='option1')
        NormalPollOption.objects.create(poll=poll, value='option2')
        UserPoll.objects.create(user=self.user1, poll=poll, choices={})
        UserPoll.objects.create(user=self.user2, poll=poll, choices={})
        self.services.finalize_poll(poll, option1)
        expected_subject = 'Polling title finished'
        expected_message = 'You can no longer vote on poll title!'
        mocked_init.assert_called_with(expected_subject, expected_message, 'info@penguin.com',
                                       ['user1@example.com', 'user2@example.com'], connection=mock.ANY)
        mocked_send.assert_called()
        self.assertEqual(True, option1.final, 'Option1 is final')
        self.assertEqual(PollStatus.CLOSED.value, poll.status, 'Poll is closed')
