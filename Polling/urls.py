from django.conf.urls import url

from Polling.views import PollManagementView, PollParticipationView

urlpatterns = [
    url(r'^(?P<poll_id>\d+)/?', PollParticipationView.as_view({'get': 'get_poll'}), name='get-poll'),
    url(r'^vote/(?P<poll_id>\d+)/?', PollParticipationView.as_view({'post': 'vote'}), name='vote'),
    url(r'^created/?', PollManagementView.as_view({'get': 'get_created_polls'}), name='get-created-polls'),
    url(r'^create/?', PollManagementView.as_view({'post': 'create_poll'}), name='create-poll'),
    url(r'^finalize/(?P<poll_id>\d+)/?', PollManagementView.as_view({'post': 'finalize'}),
        name='finalize-poll'),
    url(r'^participated/?', PollParticipationView.as_view({'get': 'get_participated_polls'}),
        name='get-participated-polls'),
    url(r'^comment/(?P<poll_id>\d+)/(?P<option_id>\d+)/?', PollParticipationView.as_view({'post': 'comment'}),
        name='comment'),
    url(r'^comments/(?P<poll_id>\d+)/(?P<option_id>\d+)/?', PollParticipationView.as_view({'get': 'get_comments'}),
        name='get_comments'),
    url(r'^edit/(?P<poll_id>\d+)?', PollManagementView.as_view({'put': 'edit_poll'}), name='edit-poll'),
]
