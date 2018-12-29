from datetime import datetime

from django.core.mail import send_mail

from Polling.enums import PollStatus, OptionStatus
from Polling.models import Poll, NormalPollOption, User, UserPoll, WeeklyPollOption
from utilities.exceptions import BusinessLogicException


class PollingServices:
    def create_poll(self, title, description, owner, option_values, participants, is_normal):
        """
        :param participants: list of username
        """
        poll = Poll.objects.create(title=title, description=description, owner=owner)
        if is_normal:
            options = NormalPollOption.objects.bulk_create(
                [NormalPollOption(poll=poll, value=option) for option in option_values]
            )
        else:
            options = WeeklyPollOption.objects.bulk_create(
                [WeeklyPollOption(poll=poll, weekday=option['weekday'], start_time=self._to_time(option['start_time']),
                                  end_time=self._to_time(option['end_time'])) for option in option_values]
            )
        users = User.objects.filter(username__in=participants)
        self._create_user_polls(users, poll, options)
        self._notify(title, users)

    @staticmethod
    def notify_with_email(users, subject, message):
        send_mail(subject, message, 'info@penguin.com', [user.email for user in users], fail_silently=True)

    def finalize_poll(self, poll, option):
        poll.status = PollStatus.CLOSED.value
        poll.save()
        users = User.objects.filter(userpoll__poll=poll)
        NormalPollOption.objects.filter(poll=poll).update(final=False)
        WeeklyPollOption.objects.filter(poll=poll).update(final=False)
        option.final = True
        option.save()
        subject = 'Polling {} finished'.format(poll.title)
        message = 'You can no longer vote on poll {}!'.format(poll.title)
        self.notify_with_email(users, subject, message)

    @staticmethod
    def _create_user_polls(users, poll, options):
        for user in users:
            UserPoll.objects.create(user=user, poll=poll, choices={
                str(option.id): OptionStatus.NO.value for option in options
            })

    def _notify(self, title, users):
        subject = 'Invitation to {} polling'.format(title)
        message = 'Please participate in the poll {} using your panel!'.format(title)
        self.notify_with_email(users, subject, message)

    @staticmethod
    def _to_time(time_str):
        return datetime.strptime(time_str, '%H:%M').time()

    def save_choices(self, poll, user_poll, options):
        self._validate_options(options, user_poll)
        self._validate_poll_not_closed(poll)
        user_poll.choices = options
        user_poll.save()

    def _validate_options(self, options, user_poll):
        if options.keys() != user_poll.choices.keys():
            raise BusinessLogicException(code='invalid_options', detail='all options must be included')
        if not set(options.values()) <= set(OptionStatus.values()):
            raise BusinessLogicException(code='invalid_options', detail='invalid option status')

    def _validate_poll_not_closed(self, poll):
        if poll.status == PollStatus.CLOSED.value:
            raise BusinessLogicException(code='poll_closed', detail='Poll is closed and you can no longer vote')
