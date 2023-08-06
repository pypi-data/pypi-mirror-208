from unittest import TestCase
from orkg import ORKG


class TestOut(TestCase):
    """
    Some test scenarios might need to be adjusted to the content of the running ORKG instance
    """

    orkg = ORKG(host="https://sandbox.orkg.org")

    def test_new_pagination_wrapper(self):
        res = self.orkg.resources.get()
        if self.orkg.pagination_activated():
            self.assertIsNotNone(res.page_info, 'pageable info is not None')
            self.assertTrue('content' not in res.content, 'content extraction performed correctly')
        else:
            self.assertIsNone(res.page_info, 'pageable info is None because back-end is not up to date')
            self.assertWarns(DeprecationWarning)

    def test_new_pagination_wrapper_on_none_get_call(self):
        label = "test"
        res = self.orkg.resources.add(label=label)
        self.assertTrue(res.succeeded)
        if self.orkg.pagination_activated():
            self.assertIsNone(res.page_info, 'pageable is not available in POST calls')
            self.assertTrue('content' not in res.content, 'content extraction performed correctly')
        else:
            self.assertIsNone(res.page_info, 'pageable is not available in POST calls even if the backend is up-to-date')
            self.assertWarns(DeprecationWarning)

