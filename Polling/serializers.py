from rest_framework import serializers

from Polling.models import Poll


class PollSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField(method_name='get_options')

    def get_options(self, obj):
        return obj.polloption_set.values_list('value', flat=True)

    class Meta:
        model = Poll
        fields = ('title', 'description', 'status', 'options')
