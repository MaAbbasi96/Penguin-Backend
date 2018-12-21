from Polling.enums import PollStatus
from Polling.models import Poll, PollOption, User, UserPoll


class PollingServices:
    def create_poll(self, title, description, owner, options, participants):
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
            self.notify(user)

    def notify(self, user):
        pass

    def finalize_poll(self, poll, option):
        poll.status = PollStatus.CLOSED.value
        poll.save()
        users = User.objects.filter(userpoll__poll=poll)
        PollOption.objects.filter(poll=poll).update(final=False)
        option.final = True
        option.save()
        for user in users:
            self.notify(user)
        print(users)
