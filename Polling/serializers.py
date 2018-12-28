from rest_framework import serializers

from Polling.enums import OptionStatus
from Polling.models import Poll, PollOption, UserPoll, User


class PollSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    final_option = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()

    def get_options(self, obj):
        options = {}
        obj.polloption_set.values_list('value', flat=True)
        for option in obj.polloption_set.all():
            option_votes = {
                'maybe': 0,
                'yes': 0
            }
            user_votes = UserPoll.objects.filter(poll=obj).values_list('choices', flat=True)
            for vote in user_votes:
                if vote[option.value] == OptionStatus.YES.value:
                    option_votes['no'] += 1
                if vote[option.value] == OptionStatus.MAYBE.value:
                    option_votes['maybe'] += 1
            options[option.value] = option_votes
        return options

    def get_final_option(self, obj):
        try:
            return obj.polloption_set.get(final=True).value
        except PollOption.DoesNotExist:
            return None

    def get_creator(self, obj):
        try:
            return User.objects.get(id=obj.owner_id).username
        except User.DoesNotExist:
            return None

    class Meta:
        model = Poll
        fields = ('id', 'title', 'description', 'status', 'options', 'final_option', 'creator')
