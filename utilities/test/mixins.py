# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import traceback
import json

from utilities.models.exceptions import BusinessLogicException


# noinspection PyPep8Naming,PyUnresolvedReferences
class AssertionsMixin(object):
    def assertObjectEqualsDict(self, dictionary, obj):
        """
        :type dictionary: dict
        """
        for key, value in dictionary.iteritems():
            obj_value = getattr(obj, key)
            self._assert_values_equal(key, value, obj_value)

    def _assert_values_equal(self, key, assertion, value):
        message = '{} does not match'.format(key)
        if type(assertion) is tuple:
            message = assertion[1]
            assertion = assertion[0]

        if type(assertion) is float:
            self.assertAlmostEqual(value, assertion, 7, message)
        else:
            self.assertEqual(value, assertion, message)

    def assertUnorderedListEqual(self, expected_list, actual_list):
        self.assertEqual(set(expected_list), set(actual_list),
                         'Content of list do not match.\n'
                         'Expected: {expected}\n'
                         'Actual: {actual}'.format(expected=set(expected_list),
                                                   actual=set(actual_list)))
        self.assertEqual(len(expected_list), len(actual_list),
                         'Some duplicate items do not match.\n'
                         'Expected: {expected}\n'
                         'Actual: {actual}'.format(expected=expected_list, actual=actual_list))

    def assertDictEqualWithoutOrdering(self, expected_dict, actual_dict):
        """
        :type expected_dict: dict or OrderedDict
        :type actual_dict: dict or OrderedDict
        """

        def ordered_dict_to_dict(ordered_dict):
            return json.loads(json.dumps(ordered_dict))

        self.assertDictEqual(ordered_dict_to_dict(expected_dict),
                             ordered_dict_to_dict(actual_dict))

    def assertRaisesBusinessLogicException(self, code):
        """
        Creates and returns an exception context manager eligible to check for expected
        BusinessLogicException and its code
        You might use this method as a with statement context
        with self.the code string which we expect the block raise BusinessLogicException
        :param code: the code string which we expect the block raise BusinessLogicException
        :return: the context manager which can be used as a with context
        """

        class ExceptionContext(object):
            def __init__(self, test_case, expected_code):
                self.test_case = test_case
                self.expected_code = expected_code

            def __enter__(self):
                pass

            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_val is None:
                    self.test_case.fail('Expected the block to raise BusinessLogicException but '
                                        'it did not raise at all')
                    return True

                if isinstance(exc_val, BusinessLogicException):
                    if exc_val.code == self.expected_code:
                        return True
                    self.test_case.fail("Expected BusinessLogicException's code to be "
                                        "{expected_code} but it is "
                                        "{actual_code}\n"
                                        "Detail: {detail}".format(expected_code=self.expected_code,
                                                                  actual_code=exc_val.code,
                                                                  detail=exc_val.detail))
                    return True

                formatted_tb = traceback.format_exception(exc_type, exc_val, exc_tb)
                self.test_case.fail(
                    'Expected the block to raise BusinessLogicException but it raised {type} '
                    'instead.\nTraceback:\n{traceback}'.format(type=exc_type,
                                                               traceback=formatted_tb))
                return True

        return ExceptionContext(test_case=self, expected_code=code)
