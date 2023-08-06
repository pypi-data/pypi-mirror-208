from unittest import TestCase
from orkg import ORKG


class TestPredicates(TestCase):
    """
    Some test scenarios might need to be adjusted to the content of the running ORKG instance
    """
    orkg = ORKG()

    def test_by_id(self):
        res = self.orkg.predicates.by_id('P1')
        self.assertTrue(res.succeeded)

    def test_get(self):
        size = 10
        res = self.orkg.predicates.get(size=size)
        self.assertTrue(res.succeeded)
        self.assertEqual(len(res.content), size)

    def test_get_unpaginated(self):
        res = self.orkg.predicates.get_unpaginated(size=500)
        self.assertTrue(res.all_succeeded)

    def test_add(self):
        label = "test predicate"
        res = self.orkg.predicates.add(label=label)
        self.assertTrue(res.succeeded)
        self.assertEqual(res.content['label'], label)

    def test_find_or_add(self):
        import random
        import string
        label = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(15))
        old = self.orkg.predicates.add(label=label)
        self.assertTrue(old.succeeded, 'Creating first predicate is a success')
        self.assertEqual(old.content['label'], label, 'The first predicate has the correct label')
        new = self.orkg.predicates.find_or_add(label=label)
        self.assertTrue(new.succeeded, 'Creating second predicate is a success')
        self.assertEqual(new.content['id'], old.content['id'], 'the two predicates have the same id')

    def test_update(self):
        res = self.orkg.predicates.add(label="Coco predicate")
        self.assertTrue(res.succeeded)
        label = "Test predicate"
        res = self.orkg.predicates.update(id=res.content['id'], label=label)
        self.assertTrue(res.succeeded)
        res = self.orkg.predicates.by_id(res.content['id'])
        self.assertTrue(res.succeeded)
        self.assertEqual(res.content['label'], label)
