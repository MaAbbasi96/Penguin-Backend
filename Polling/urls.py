from django.conf.urls import url

from Polling.views import PollView


urlpatterns = [
    url(r'^(?P<poll_id>\d+)/?', PollView.as_view({'get': 'get_poll'}), name='get-poll'),
    url(r'^create/?', PollView.as_view({'post': 'create'}), name='create-poll'),
    url(r'^finalize/(?P<poll_id>\d+)/?', PollView.as_view({'post': 'finalize'}),
        name='finalize-poll'),
    url(r'^', PollView.as_view({'get': 'get_poll_list'}), name='get-poll-list'),
]
