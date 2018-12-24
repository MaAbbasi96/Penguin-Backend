import json
import logging
import traceback
from abc import abstractmethod

from django.core.urlresolvers import resolve
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIRequestFactory, APIClient

from utilities.test.abc_test_meta import ABCTestMeta
from utilities.test.mixins import AssertionsMixin

ABCTestMeta.add_ignored_test_class_name('BaseViewTest')


class BaseViewTest(AssertionsMixin, APITestCase):
    __metaclass__ = ABCTestMeta
    docs_store = {}
    current_test_name = None
    current_test_doc = None

    def setUp(self):
        super(BaseViewTest, self).setUp()
        self.api_client = APIClient()
        self.factory = APIRequestFactory()

    @abstractmethod
    def _make_url(self, kwargs=None):
        raise NotImplementedError()

    def test_resolves_view(self, *_):
        self.assertIsNotNone(resolve(self._make_url(self._get_default_url_kwargs())))

    def _get_default_url_kwargs(self):
        return None

    def test_calling_endpoint(self, *_):
        try:
            response = self.api_client.get(self._make_url(self._get_default_url_kwargs()))
            self.assertNotEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        except Exception:
            traceback.print_exc()
            self.fail("Something caused request to endpoint to raise an exception.")

    def assertStatus(self, response, expected):
        msg = 'Expected status code of response to equal {status}'.format(status=expected)
        if hasattr(response, 'data'):
            msg += '\nResponse data is {data}'.format(data=response.data)
        self.assertEquals(response.status_code, expected, msg)

    def assertSuccess(self, response, expected_status_code=None):
        data_appendix = ''
        if hasattr(response, 'data'):
            data_appendix = 'Response data is {data}'.format(data=response.data)
        if expected_status_code is None:
            self.assertIn(
                response.status_code, [
                    status.HTTP_200_OK,
                    status.HTTP_201_CREATED,
                ],
                """
                200 or 201 status code should get returned
                {response_data}
                """.format(response_data=data_appendix)
            )
        else:
            self.assertEqual(
                response.status_code, expected_status_code,
                'Status could should have been {code}'.format(code=expected_status_code) +
                data_appendix
            )

    def _get_for_response(self, user=None, data=None, url_kwargs=None, docs=True, **extra):
        return self.__request_for_response(self.api_client.get, user=user, data=data,
                                           url_kwargs=url_kwargs, format='json', docs=docs,
                                           extra=extra)

    def _post_for_response(self, user=None, data=None, url_kwargs=None, format='json',
                           docs=True, **extra):
        return self.__request_for_response(self.api_client.post, user=user, data=data,
                                           url_kwargs=url_kwargs, format=format, docs=docs,
                                           extra=extra)

    def _put_for_response(self, user=None, data=None, url_kwargs=None, format='json', docs=True,
                          **extra):
        return self.__request_for_response(self.api_client.put, user=user, data=data,
                                           url_kwargs=url_kwargs, format=format, docs=docs,
                                           extra=extra)

    def _delete_for_response(self, user=None, data=None, url_kwargs=None, format='json',
                             docs=True, **extra):
        return self.__request_for_response(self.api_client.delete, user=user, data=data,
                                           url_kwargs=url_kwargs, format=format, docs=docs,
                                           extra=extra)

    def __request_for_response(self, method, user=None, data=None, url_kwargs=None, format='json',
                               docs=True, extra=None):
        extra = extra or {}
        self.__set_auth(user)
        headers = self._modify_headers(extra)
        if method == self.api_client.get:
            response = method(self._make_url(kwargs=url_kwargs), data=data, **headers)
        else:
            response = method(
                self._make_url(kwargs=url_kwargs), data=data, format=format, **headers)
        if not docs or format != 'json':
            return response
        self._generate_docs(response, method, data, url_kwargs, format, headers)
        return response

    def _ensure_json_serializable(self, obj, fail_silently=True):
        try:
            json.dumps(obj)
            return obj
        except Exception as err:
            logging.error(err)
            if not fail_silently:
                raise
            return None

    def _generate_docs(self, response, method, data, url_kwargs, format, headers):
        app_name = self.__class__.__module__.split('.')[0]
        url_entry = self.docs_store.get(app_name, {}).get(self._make_url(url_kwargs), [])
        method_name = {
            self.api_client.get: 'get',
            self.api_client.post: 'post',
            self.api_client.delete: 'delete',
            self.api_client.patch: 'patch',
            self.api_client.put: 'put'
        }[method]
        response_data = response.data if hasattr(response, 'data') else {}
        url_entry.append({
            'method': method_name,
            'data': self._ensure_json_serializable(data),
            'url_kwargs': self._ensure_json_serializable(url_kwargs),
            'format': format,
            'headers': headers,
            'permissions': self._ensure_json_serializable(self._get_permission_classes_for_docs()),
            'meta': {
                'name': self.current_test_name,
                'docs': self.current_test_doc,
            },
            'response': {
                'data': self._ensure_json_serializable(response_data),
                'status': response.status_code,
            }
        })
        self.docs_store[app_name] = self.docs_store.get(app_name, {})
        self.docs_store[app_name][self._make_url(url_kwargs)] = url_entry

    def _get_permission_classes_for_docs(self):
        return None

    def _modify_headers(self, headers):
        return {
            'HTTP_' + k.upper().replace('-', '_'): v for k, v in headers.iteritems()
        }

    def __set_auth(self, user):
        if user is None:
            self.api_client.credentials(HHTTP_AUTHORIZATION=None)
            return
        try:
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    @abstractmethod
    def _get_view_class(self):
        raise NotImplementedError

    def __getattribute__(self, item):
        result = super(BaseViewTest, self).__getattribute__(item)
        if item and callable(result) and item.startswith('test'):
            BaseViewTest.current_test_doc = result.__doc__
            BaseViewTest.current_test_name = result.__name__
        return result
