import datetime
from unittest import mock

from django.core.mail import EmailMultiAlternatives
from django.test import TestCase

from Polling.enums import PollStatus, OptionStatus
from Polling.models import User, Poll, NormalPollOption, UserPoll, WeeklyPollOption
from Polling.services import PollingServices
from utilities.exceptions import BusinessLogicException


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
                                  [self.user1, self.user2, ], True, None)
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
        self.assertEqual(4, UserPoll.objects.all().count())

    def test_create_weekly_poll(self, mocked_init, mocked_send):
        self.assertEqual(0, Poll.objects.all().count())
        self.assertEqual(0, WeeklyPollOption.objects.all().count())
        self.assertEqual(0, UserPoll.objects.all().count())
        options = [
            {'weekday': 0, 'start_time': '15:30', 'end_time': '16:30'},
            {'weekday': 1, 'start_time': '16:30', 'end_time': '17:30'},
        ]
        self.services.create_poll(self.title, self.description, self.owner, options, [self.user1, self.user2, ],
                                  False, None)
        mocked_send.assert_called()
        mocked_init.assert_called()
        self.assertEqual(1, Poll.objects.all().count())
        self.assertEqual(self.owner, Poll.objects.first().owner)
        self.assertEqual(2, WeeklyPollOption.objects.all().count())
        self.assertListEqual([
            {'weekday': 0, 'start_time': datetime.time(15, 30), 'end_time': datetime.time(16, 30)},
            {'weekday': 1, 'start_time': datetime.time(16, 30), 'end_time': datetime.time(17, 30)},
        ], list(WeeklyPollOption.objects.all().values('weekday', 'start_time', 'end_time')))
        self.assertEqual(4, UserPoll.objects.all().count())

    def test_finalize_poll(self, mocked_init, mocked_send):
        poll = Poll.objects.create(owner=self.owner, title=self.title, description=self.description)
        option1 = NormalPollOption.objects.create(poll=poll, value='option1')
        NormalPollOption.objects.create(poll=poll, value='option2')
        UserPoll.objects.create(user=self.user1, poll=poll, choice={})
        UserPoll.objects.create(user=self.user2, poll=poll, choice={})
        self.services.finalize_poll(poll, option1)
        expected_subject = 'Polling title finished'
        expected_message = 'You can no longer vote on poll title!'
        mocked_init.assert_called_with(expected_subject, expected_message, 'info@penguin.com',
                                       ['user1@example.com', 'user2@example.com'], connection=mock.ANY)
        mocked_send.assert_called()
        self.assertEqual(True, option1.final, 'Option1 is final')
        self.assertEqual(PollStatus.CLOSED.value, poll.status, 'Poll is closed')

    def test_save_choices(self, *_):
        poll = Poll.objects.create(owner=self.owner, title=self.title, description=self.description)
        poll_option = NormalPollOption.objects.create(value='option1', poll=poll)
        user_poll = UserPoll.objects.create(user=self.user1, poll=poll,
                                            choice={str(poll_option.id): OptionStatus.NO.value})
        self.services.save_choices(poll, [user_poll], {str(poll_option.id): OptionStatus.YES.value})
        self.assertDictEqual({str(poll_option.id): OptionStatus.YES.value},
                             UserPoll.objects.get(id=user_poll.id).choice)

    def test_save_choices_with_invalid_options(self, *_):
        poll = Poll.objects.create(owner=self.owner, title=self.title, description=self.description)
        poll_option = NormalPollOption.objects.create(value='option1', poll=poll)
        user_poll = UserPoll.objects.create(user=self.user1, poll=poll,
                                            choice={str(poll_option.id): OptionStatus.NO.value})
        self.assertRaises(BusinessLogicException,
                          self.services.save_choices, poll, [user_poll], {str(poll_option.id): 3})

    def test_save_choices_with_closed_poll(self, *_):
        poll = Poll.objects.create(owner=self.owner, title=self.title, description=self.description,
                                   status=PollStatus.CLOSED.value)
        poll_option = NormalPollOption.objects.create(value='option1', poll=poll)
        user_poll = UserPoll.objects.create(user=self.user1, poll=poll,
                                            choice={str(poll_option.id): OptionStatus.NO.value})
        self.assertRaises(BusinessLogicException,
                          self.services.save_choices, poll, [user_poll], {str(poll_option.id): OptionStatus.YES.value})

    def test_save_choices_with_overlap(self, *_):
        poll1 = Poll.objects.create(owner=self.owner, title=self.title, description=self.description, is_normal=False)
        poll2 = Poll.objects.create(owner=self.owner, title=self.title, description=self.description, is_normal=False)
        poll_option1 = WeeklyPollOption.objects.create(poll=poll1, weekday=0, start_time=datetime.time(16, 30),
                                                       end_time=datetime.time(18, 30))
        poll_option2 = WeeklyPollOption.objects.create(poll=poll2, weekday=0, start_time=datetime.time(17, 30),
                                                       end_time=datetime.time(19, 30))
        UserPoll.objects.create(user=self.user1, poll=poll1,
                                choice={str(poll_option1.id): OptionStatus.YES.value})
        user_poll2 = UserPoll.objects.create(user=self.user1, poll=poll2,
                                             choice={str(poll_option2.id): OptionStatus.NO.value})
        self.assertRaises(BusinessLogicException,
                          self.services.save_choices, poll2, [user_poll2], {str(poll_option2.id): OptionStatus.YES.value})
