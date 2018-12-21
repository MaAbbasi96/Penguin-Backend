from rest_framework.viewsets import ViewSet


class PollView(ViewSet):
    def create(self, request):
        print('create')

    def get_poll_list(self, request):
        print('get_poll_list')

    def finalize(self, request, poll_id):
        print('finalize', poll_id)

    def get_poll(self, request, poll_id):
        print('get_poll', poll_id)
