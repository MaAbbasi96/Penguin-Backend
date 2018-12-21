from rest_framework import serializers

from Polling.models import Poll, PollOption


class PollSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    final_option = serializers.SerializerMethodField()

    def get_options(self, obj):
        return obj.polloption_set.values_list('value', flat=True)

    def get_final_option(self, obj):
        try:
            return obj.polloption_set.get(final=True).value
        except PollOption.DoesNotExist:
            return None

    class Meta:
        model = Poll
        fields = ('title', 'description', 'status', 'options', 'final_option')
