from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status

from utilities.exceptions import BusinessLogicException


class ApplicationExceptionMiddleware(MiddlewareMixin):
    # noinspection PyMethodMayBeStatic
    def process_exception(self, _, e):
        if isinstance(e, BusinessLogicException):
            return HttpResponse('{}, {}'.format(e.code, e.detail), status=status.HTTP_409_CONFLICT)
