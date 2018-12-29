from datetime import datetime

from django.core.mail import send_mail

from Polling.enums import PollStatus, OptionStatus
from Polling.models import Poll, NormalPollOption, User, UserPoll, WeeklyPollOption


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
        return datetime.strptime(time_str, '%I:%M').time()
