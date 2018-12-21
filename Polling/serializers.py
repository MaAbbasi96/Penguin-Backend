from rest_framework import serializers

from Polling.models import Poll, PollOption, UserPoll


class PollSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    final_option = serializers.SerializerMethodField()

    def get_options(self, obj):
        options = {}
        obj.polloption_set.values_list('value', flat=True)
        for option in obj.polloption_set.all():
            count = 0
            user_votes = UserPoll.objects.filter(poll=obj).values_list('choices', flat=True)
            for vote in user_votes:
                if vote[option.value]:
                    count += 1
            options[option.value] = count
        return options

    def get_final_option(self, obj):
        try:
            return obj.polloption_set.get(final=True).value
        except PollOption.DoesNotExist:
            return None

    class Meta:
        model = Poll
        fields = ('id', 'title', 'description', 'status', 'options', 'final_option')
