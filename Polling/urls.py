from django.conf.urls import url

from Polling.views import PollManagementView, PollParticipationView

urlpatterns = [
    url(r'^(?P<poll_id>\d+)/?', PollParticipationView.as_view({'get': 'get_poll'}), name='get-poll'),
    url(r'^created/?', PollManagementView.as_view({'get': 'get_created_polls'}), name='get-created-polls'),
    url(r'^create/?', PollManagementView.as_view({'post': 'create'}), name='create-poll'),
    url(r'^finalize/(?P<poll_id>\d+)/?', PollManagementView.as_view({'post': 'finalize'}),
        name='finalize-poll'),
    url(r'^participated/?', PollParticipationView.as_view({'get': 'get_participated_polls'}),
        name='get-participated-polls'),
]
