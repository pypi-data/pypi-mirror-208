from unittest import TestCase

from orkg.out import OrkgUnpaginatedResponse, OrkgResponse
from tests.mock.mock_pageable import mock_pageable_response


class TestOrkgUnpaginatedResponse(TestCase):

    def test_content_is_extended(self):
        status_code = 200
        content_size = 4
        base_response = mock_pageable_response(status_code=status_code, content_size=content_size)
        responses = [
            OrkgResponse(response=base_response, status_code=None, content=None, url='test_url', paged=True),
            OrkgResponse(response=base_response, status_code=None, content=None, url='test_url', paged=True)
        ]

        response = OrkgUnpaginatedResponse(responses=responses)
        self.assertTrue(len(response.responses) == len(responses))
        self.assertTrue(response.all_succeeded)
        self.assertTrue(len(response.content) == content_size * len(response.responses))

