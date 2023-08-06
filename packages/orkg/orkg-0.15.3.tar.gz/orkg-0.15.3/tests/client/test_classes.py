from unittest import TestCase
from orkg import ORKG


class TestClasses(TestCase):
    """
    Some test scenarios might need to be adjusted to the content of the running ORKG instance
    """
    orkg = ORKG()

    def test_by_id(self):
        res = self.orkg.classes.by_id('Paper')
        self.assertTrue(res.succeeded)

    def test_get(self):
        res = self.orkg.classes.get_all()
        self.assertTrue(res.succeeded)

    def test_get_with_term(self):
        term = 'Paper'
        res = self.orkg.classes.get_all(q=term)
        self.assertTrue(res.succeeded)

    def test_get_resources_by_class(self):
        term = 'Paper'
        res = self.orkg.classes.get_resource_by_class(class_id=term)
        self.assertTrue(res.succeeded)

    def test_get_resources_by_class_unpaginated(self):
        term = 'Paper'
        res = self.orkg.classes.get_resource_by_class_unpaginated(class_id=term)
        self.assertTrue(res.all_succeeded)

    def test_get_resources_by_class_with_items(self):
        term = 'Paper'
        res = self.orkg.classes.get_resource_by_class(class_id=term, size=30)
        self.assertTrue(res.succeeded)
        self.assertEqual(len(res.content), 30)

    def test_get_resources_by_class_with_query(self):
        clazz = 'Problem'
        term = "Machine"
        res = self.orkg.classes.get_resource_by_class(class_id=clazz, q=term)
        self.assertTrue(res.succeeded)
        self.assertTrue(all(term.lower().strip() in resource['label'].lower().strip()
                            for resource in res.content))

    def test_add(self):
        label = "Class Z"
        res = self.orkg.classes.add(label=label)
        self.assertTrue(res.succeeded)
        self.assertEqual(res.content['label'], label)

    def test_find_or_add(self):
        import random
        import string
        label = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(15))
        old = self.orkg.classes.add(label=label)
        self.assertTrue(old.succeeded, 'Creating first class is a success')
        self.assertEqual(old.content['label'], label, 'The first class has the correct label')
        new = self.orkg.classes.find_or_add(label=label)
        self.assertTrue(new.succeeded, 'Creating second class is a success')
        self.assertEqual(new.content['id'], old.content['id'], 'the two classes have the same id')

    def test_update(self):
        res = self.orkg.classes.add(label="Class A")
        self.assertTrue(res.succeeded)
        label = "Class B"
        res = self.orkg.classes.update(id=res.content['id'], label=label)
        self.assertTrue(res.succeeded)
        res = self.orkg.classes.by_id(res.content['id'])
        self.assertTrue(res.succeeded)
        self.assertEqual(res.content['label'], label)
