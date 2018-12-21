from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from Polling.models import Poll, User
from Polling.serializers import PollSerializer
from utilities.request import RequestWrapper


class PollView(ViewSet):
    def create(self, request):
        print('create')

    def get_poll_list(self, request):
        print('get_poll_list')

    def finalize(self, request, poll_id):
        print('finalize', poll_id)

    def get_poll(self, request, poll_id):
        wrapper = RequestWrapper(request)
        username = wrapper.get_query_param('username')
        get_object_or_404(User, username=username)
        poll = get_object_or_404(Poll, id=poll_id)
        return Response(PollSerializer(poll).data)
