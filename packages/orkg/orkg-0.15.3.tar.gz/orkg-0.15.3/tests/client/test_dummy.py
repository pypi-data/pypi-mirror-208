from unittest import TestCase
from orkg import ORKG


class TestDummy(TestCase):
    """
    Some test scenarios might need to be adjusted to the content of the running ORKG instance
    """

    orkg = ORKG()

    def test_200_dummy(self):
        fake_content = {'orkg': 'super easy'}
        resp = self.orkg.dummy.create_200_response(content=fake_content)
        self.assertTrue(resp.succeeded)
        self.assertEqual(resp.content, fake_content)

    def test_404_dummy(self):
        fake_content = [{'msg': 'bad content'}]
        resp = self.orkg.dummy.create_404_response(content=fake_content)
        self.assertFalse(resp.succeeded)
        self.assertEqual(resp.content, fake_content)

    def test_generic_dummy(self):
        fake_content = {'error': 'server died'}
        fake_code = '500'
        resp = self.orkg.dummy.create_xxx_response(code=fake_code, content=fake_content)
        self.assertFalse(resp.succeeded)
        self.assertEqual(resp.status_code, fake_code)


