from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.viewsets import ViewSet

from Polling.enums import PollStatus
from Polling.models import Poll, User, PollOption, UserPoll
from Polling.serializers import PollSerializer
from utilities.request import RequestWrapper
from Polling.services import PollingServices


class PollManagementView(ViewSet):
    def create(self, request):
        wrapper = RequestWrapper(request)
        username = wrapper.get_body_param('username')
        title = wrapper.get_body_param('title')
        description = wrapper.get_body_param('description')
        options = wrapper.get_body_param('options')
        participants = wrapper.get_body_param('participants')
        print(username, title, description, options, participants)
        user = get_object_or_404(User, username=username)
        PollingServices().create_poll(title, description, user, options, participants)
        return Response(status=HTTP_200_OK)

    def get_created_polls(self, request):
        wrapper = RequestWrapper(request)
        username = wrapper.get_query_param('username')
        user = get_object_or_404(User, username=username)
        polls = Poll.objects.filter(owner=user)
        return Response(PollSerializer(polls, many=True).data)

    def finalize(self, request, poll_id):
        wrapper = RequestWrapper(request)
        username = wrapper.get_body_param('username')
        option_value = wrapper.get_body_param('option')
        user = get_object_or_404(User, username=username)
        poll = get_object_or_404(Poll, id=poll_id, owner=user)
        option = get_object_or_404(PollOption, poll=poll, value=option_value)
        PollingServices().finalize_poll(poll, option)
        return Response(status=HTTP_200_OK)


class PollParticipationView(ViewSet):
    def get_participated_polls(self, request):
        wrapper = RequestWrapper(request)
        username = wrapper.get_query_param('username')
        user = get_object_or_404(User, username=username)
        polls = Poll.objects.filter(userpoll__user=user)
        return Response(PollSerializer(polls, many=True).data)

    def get_poll(self, request, poll_id):
        wrapper = RequestWrapper(request)
        username = wrapper.get_query_param('username')
        # print(username, poll_id)
        user = get_object_or_404(User, username=username)
        poll = get_object_or_404(Poll, id=poll_id)
        get_object_or_404(UserPoll, user=user, poll=poll)
        return Response(PollSerializer(poll).data)

    def vote(self, request, poll_id):
        wrapper = RequestWrapper(request)
        username = wrapper.get_body_param('username')
        user = get_object_or_404(User, username=username)
        options = wrapper.get_body_param('options')
        # print(options, type(options))
        poll = get_object_or_404(Poll, id=poll_id)
        user_poll = get_object_or_404(UserPoll, user=user, poll=poll)
        final_option = poll.polloption_set.filter(final=True)
        if not final_option:
            return Response(HTTP_400_BAD_REQUEST)
        user_poll.choices = options
        user_poll.save()
        return Response(status=HTTP_200_OK)
