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
            poll.is_normal = False
            poll.save()
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
            for option in options:
                UserPoll.objects.create(user=user, poll=poll, choice={
                    str(option.id): OptionStatus.NO.value
                })

    def _notify(self, title, users):
        subject = 'Invitation to {} polling'.format(title)
        message = 'Please participate in the poll {} using your panel!'.format(title)
        self.notify_with_email(users, subject, message)

    @staticmethod
    def _to_time(time_str):
        return datetime.strptime(time_str, '%H:%M').time()

    def save_choices(self, poll, user_polls, options):
        self._validate_options(options, user_polls)
        self._validate_poll_not_closed(poll)
        # user_poll.choices = options.
        if user_polls[0].poll.weeklypolloption_set.exists():
            self._validate_overlap(user_polls, options)
        for user_poll in user_polls:
            for option in options.keys():
                if option in user_poll.choice.keys():
                    user_poll.choice = {
                        option: options.get(option)
                    }
            user_poll.save()

    def _validate_options(self, options, user_polls):
        if list(options.keys()) != [list(user_poll.choice.keys())[0] for user_poll in user_polls]:
            raise BusinessLogicException(code='invalid_options', detail='all options must be included')
        if not set(options.values()) <= set(OptionStatus.values()):
            raise BusinessLogicException(code='invalid_options', detail='invalid option status')

    def _validate_poll_not_closed(self, poll):
        if poll.status == PollStatus.CLOSED.value:
            raise BusinessLogicException(code='poll_closed', detail='Poll is closed and you can no longer vote')

    def _validate_overlap(self, user_polls_to_check, new_options):
        option_ids = []
        current_options = self._filter_keys(new_options)
        for user_poll_to_check in user_polls_to_check:
            for user_poll in UserPoll.objects.filter(user=user_poll_to_check.user, poll__is_normal=False):
                if user_poll_to_check.poll == user_poll.poll:
                    continue
                option_ids += (self._filter_keys(user_poll.choice))
        option_ids = list(set(option_ids))
        options_to_check = WeeklyPollOption.objects.filter(id__in=current_options)
        options = WeeklyPollOption.objects.filter(id__in=option_ids)
        for option_to_check in options_to_check:
            for option in options:
                if option_to_check.weekday == option.weekday and \
                        (
                            (option_to_check.end_time > option.start_time
                                and option_to_check.start_time < option.end_time)
                            or
                            (option.end_time > option_to_check.start_time
                                and option.start_time < option_to_check.end_time)
                        ):
                    raise BusinessLogicException(code='overlap', detail='You have voted for another poll for this time')

    @staticmethod
    def _filter_keys(dictionary):
        result = []
        for key in dictionary:
            if dictionary[key] == OptionStatus.YES.value or dictionary[key] == OptionStatus.MAYBE.value:
                result.append(int(key))
        return result
