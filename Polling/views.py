from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet

from Polling.enums import PollStatus, OptionStatus
from Polling.models import Poll, User, UserPoll, NormalPollOption, WeeklyPollOption
from Polling.serializers import PollSerializer
from utilities.exceptions import BusinessLogicException
from utilities.request import RequestWrapper
from Polling.services import PollingServices


class PollManagementView(ViewSet):
    def create_poll(self, request):
        wrapper = RequestWrapper(request)
        username = wrapper.get_body_param('username')
        title = wrapper.get_body_param('title')
        description = wrapper.get_body_param('description')
        options = wrapper.get_body_param('options')
        participants = wrapper.get_body_param('participants')
        is_normal = wrapper.get_body_param('is_normal')
        user = get_object_or_404(User, username=username)
        PollingServices().create_poll(title, description, user, options, participants, is_normal)
        return Response(status=status.HTTP_200_OK)

    def get_created_polls(self, request):
        wrapper = RequestWrapper(request)
        username = wrapper.get_query_param('username')
        user = get_object_or_404(User, username=username)
        polls = Poll.objects.filter(owner=user)
        return Response(PollSerializer(polls, many=True).data)

    def finalize(self, request, poll_id):
        wrapper = RequestWrapper(request)
        username = wrapper.get_body_param('username')
        option_id = wrapper.get_body_param('option')
        user = get_object_or_404(User, username=username)
        poll = get_object_or_404(Poll, id=poll_id, owner=user)
        try:
            option = NormalPollOption.objects.filter(poll=poll, id=option_id)
        except NormalPollOption.DoesNotExist:
            option = get_object_or_404(WeeklyPollOption, poll=poll, id=option_id)
        PollingServices().finalize_poll(poll, option)
        return Response(status=status.HTTP_200_OK)


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
        user = get_object_or_404(User, username=username)
        poll = get_object_or_404(Poll, id=poll_id)
        user_poll = UserPoll.objects.filter(user=user, poll=poll)
        if not user_poll and user != poll.owner:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(PollSerializer(poll).data)

    def _validate_options(self, options, user_poll):
        if options.keys() != user_poll.choices.keys():
            raise BusinessLogicException(code='invalid_options', detail='all options must be included')
        if not set(options.values()) <= set(OptionStatus.values()):
            raise BusinessLogicException(code='invalid_options', detail='invalid option status')

    def _validate_poll_not_closed(self, poll):
        if poll.status == PollStatus.CLOSED.value:
            raise BusinessLogicException(code='poll_closed', detail='Poll is closed and you can no longer vote')

    def vote(self, request, poll_id):
        wrapper = RequestWrapper(request)
        username = wrapper.get_body_param('username')
        user = get_object_or_404(User, username=username)
        options = wrapper.get_body_param('options')
        poll = get_object_or_404(Poll, id=poll_id)
        user_poll = get_object_or_404(UserPoll, user=user, poll=poll)
        self._validate_options(options, user_poll)
        self._validate_poll_not_closed(poll)
        user_poll.choices = options
        user_poll.save()
        return Response(status=status.HTTP_200_OK)
