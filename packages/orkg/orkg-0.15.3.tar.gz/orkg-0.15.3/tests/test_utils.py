from unittest import TestCase

from orkg.utils import NamespacedClient
from tests.mock.mock_pageable import mock_unpageable_func, mock_pageable_func, mock_unpageable_func_different_signature


class TestNamespacedClient(TestCase):

    def test_call_pageable_with_no_paging_info_should_fail(self):

        # test unpageable func with different signature
        with self.assertRaises(ValueError):
            NamespacedClient._call_pageable(
                mock_unpageable_func_different_signature,
                args={
                    'id': 'C1234'
                },
                params={}
            )

        # test unpageable func with same signature and unpageable response
        with self.assertRaises(ValueError):
            NamespacedClient._call_pageable(
                mock_unpageable_func,
                args={},
                params={}
            )

    def test_call_pageable_should_succeed(self):
        content_size = 5
        total_pages = 25

        response = NamespacedClient._call_pageable(
            mock_pageable_func,
            args={},
            params={
                'content_size': content_size,
                'total_pages': total_pages
            }
        )

        self.assertTrue(response.all_succeeded)
        self.assertEqual(len(response.responses), total_pages)
        self.assertEqual(len(response.content), content_size * total_pages)

    def test_call_pageable_with_limits_should_succeed(self):
        content_size = 5
        total_pages = 25
        start_page = 5
        end_page = 10

        response = NamespacedClient._call_pageable(
            mock_pageable_func,
            args={},
            params={
                'content_size': content_size,
                'total_pages': total_pages
            },
            start_page=start_page,
            end_page=end_page
        )

        self.assertTrue(response.all_succeeded)
        self.assertEqual(len(response.responses), end_page - start_page)
        self.assertEqual(len(response.content), content_size * (end_page - start_page))



