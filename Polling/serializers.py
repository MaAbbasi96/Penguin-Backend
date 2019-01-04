from rest_framework import serializers

from Polling.enums import OptionStatus
from Polling.models import Poll, NormalPollOption, UserPoll, User, WeeklyPollOption, Comment


class PollSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    final_option = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()

    @staticmethod
    def _get_option_votes(obj, option):
        option_votes = {
            'value': str(option),
            'maybe': 0,
            'yes': 0
        }
        user_votes = UserPoll.objects.filter(poll=obj).values_list('choice', flat=True)
        # print(user_votes)
        for vote in user_votes:
            # print(vote, option, str(option.id) in vote)
            if str(option.id) in vote:
                if vote[str(option.id)] == OptionStatus.YES.value:
                    option_votes['yes'] += 1
                if vote[str(option.id)] == OptionStatus.MAYBE.value:
                    option_votes['maybe'] += 1
        return option_votes

    def get_options(self, obj):
        options = {}
        for option in obj.normalpolloption_set.all():
            options[str(option.id)] = self._get_option_votes(obj, option)
        for option in obj.weeklypolloption_set.all():
            options[str(option.id)] = self._get_option_votes(obj, option)
        return options

    def get_final_option(self, obj):
        try:
            return obj.normalpolloption_set.get(final=True).value
        except NormalPollOption.DoesNotExist:
            try:
                return obj.weeklypolloption_set.get(final=True).value
            except WeeklyPollOption.DoesNotExist:
                return None

    def get_creator(self, obj):
        try:
            return User.objects.get(id=obj.owner_id).username
        except User.DoesNotExist:
            return None

    class Meta:
        model = Poll
        fields = ('id', 'title', 'description', 'status', 'options', 'final_option', 'creator', 'is_normal')


class CommentSerializer(serializers.ModelSerializer):
    option_id = serializers.SerializerMethodField()

    def get_option_id(self, obj):
        return list(UserPoll.objects.get(id=obj.option_id).choice.keys())[0]

    class Meta:
        model = Comment
        fields = ('id', 'message', 'date', 'user', 'option_id', 'parent')
