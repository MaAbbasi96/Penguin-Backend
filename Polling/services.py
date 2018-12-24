from django.core.mail import send_mail

from Polling.enums import PollStatus
from Polling.models import Poll, PollOption, User, UserPoll


class PollingServices:
    def create_poll(self, title, description, owner, options, participants):
        # print(options, participants)
        """
        :param participants: list of usernames
        """
        users = User.objects.filter(username__in=participants)
        poll = Poll.objects.create(title=title, description=description, owner=owner)
        PollOption.objects.bulk_create([PollOption(poll=poll, value=item_option) for item_option in options])
        for user in users:
            UserPoll.objects.create(user=user, poll=poll, choices={
                option: False for option in options
            })
        subject = 'Invitation to {} polling'.format(title)
        message = 'Please participate in the poll {} using your panel!'.format(title)
        self.notify(users, subject, message)

    @staticmethod
    def notify(users, subject, message):
        send_mail(subject, message, 'info@penguin.com', [user.email for user in users], fail_silently=True)

    def finalize_poll(self, poll, option):
        poll.status = PollStatus.CLOSED.value
        poll.save()
        users = User.objects.filter(userpoll__poll=poll)
        PollOption.objects.filter(poll=poll).update(final=False)
        option.final = True
        option.save()
        subject = 'Polling {} finished'.format(poll.title)
        message = 'You can no longer vote on poll {}!'.format(poll.title)
        self.notify(users, subject, message)
        # print(users)
