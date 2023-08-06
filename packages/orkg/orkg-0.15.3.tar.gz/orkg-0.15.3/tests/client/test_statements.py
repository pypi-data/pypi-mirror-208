from unittest import TestCase
from orkg import ORKG


class TestStatements(TestCase):
    """
    Some test scenarios might need to be adjusted to the content of the running ORKG instance
    """
    orkg = ORKG()

    def test_by_id(self):
        res = self.orkg.statements.by_id('S1')
        self.assertTrue(res.succeeded)

    def test_get(self):
        size = 10
        res = self.orkg.statements.get(size=size)
        self.assertTrue(res.succeeded)
        self.assertEqual(len(res.content), size)

    def test_get_unpaginated(self):
        size = 500
        res = self.orkg.statements.get_unpaginated(size=size, end_page=5)
        self.assertTrue(res.all_succeeded)
        self.assertTrue(len(res.responses) > 1)

    def test_get_by_subject(self):
        size = 10
        subject_id = 'R180000'
        res = self.orkg.statements.get_by_subject(subject_id=subject_id, size=size)
        self.assertTrue(res.succeeded)

    def test_get_by_subject_unpaginated(self):
        size = 10
        subject_id = 'R180000'
        res = self.orkg.statements.get_by_subject_unpaginated(subject_id=subject_id, size=size, end_page=5)
        self.assertTrue(res.all_succeeded)
        self.assertTrue(len(res.responses) > 1)

    def test_get_by_predicate(self):
        size = 10
        predicate_id = 'P22'
        res = self.orkg.statements.get_by_predicate(predicate_id=predicate_id, size=size)
        self.assertTrue(res.succeeded)

    def test_get_by_predicate_unpaginated(self):
        size = 10
        predicate_id = 'P26'
        res = self.orkg.statements.get_by_predicate_unpaginated(predicate_id=predicate_id, size=size, end_page=5)
        self.assertTrue(res.all_succeeded)
        self.assertTrue(len(res.responses) > 1)

    def test_get_by_object(self):
        size = 10
        object_id = 'R57'
        res = self.orkg.statements.get_by_object(object_id=object_id, size=size)
        self.assertTrue(res.succeeded)

    def test_get_by_object_unpaginated(self):
        size = 10
        object_id = 'R57'
        res = self.orkg.statements.get_by_object_unpaginated(object_id=object_id, size=size, end_page=5)
        self.assertTrue(res.all_succeeded)
        self.assertTrue(len(res.responses) > 1)

    def test_get_by_object_and_predicate(self):
        size = 10
        object_id = 'R57'
        predicate_id = 'P30'
        res = self.orkg.statements.get_by_object_and_predicate(
            object_id=object_id, predicate_id=predicate_id, size=size
        )
        self.assertTrue(res.succeeded)

    def test_get_by_object_and_predicate_unpaginated(self):
        size = 10
        object_id = 'R57'
        predicate_id = 'P30'
        res = self.orkg.statements.get_by_object_and_predicate_unpaginated(
            object_id=object_id, predicate_id=predicate_id, size=size
        )
        self.assertTrue(res.all_succeeded)
        self.assertTrue(len(res.responses) > 1)

    def test_get_by_subject_and_predicate(self):
        size = 10
        subject_id = 'R180000'
        predicate_id = 'compareContribution'
        res = self.orkg.statements.get_by_subject_and_predicate(
            subject_id=subject_id, predicate_id=predicate_id, size=size
        )
        self.assertTrue(res.succeeded)

    def test_get_by_subject_and_predicate_unpaginated(self):
        size = 10
        subject_id = 'R180000'
        predicate_id = 'compareContribution'
        res = self.orkg.statements.get_by_subject_and_predicate_unpaginated(
            subject_id=subject_id, predicate_id=predicate_id, size=size
        )
        self.assertTrue(res.all_succeeded)
        self.assertTrue(len(res.responses) > 1)

    def test_add(self):
        subject = self.orkg.resources.add(label="ORKG Subject").content['id']
        predicate = self.orkg.predicates.add(label="ORKG Predicate").content['id']
        object = self.orkg.literals.add(label="ORKG Object").content['id']
        res = self.orkg.statements.add(subject_id=subject, predicate_id=predicate, object_id=object)
        self.assertTrue(res.succeeded)

    def test_update(self):
        st_id = 'S1'
        new_p_id = 'P1'
        res = self.orkg.statements.update(id=st_id, predicate_id=new_p_id)
        self.assertTrue(res.succeeded)
        res = self.orkg.statements.by_id(st_id)
        self.assertTrue(res.succeeded)
        self.assertEqual(res.content['predicate']['id'], new_p_id)

    def test_exists(self):
        found = self.orkg.statements.exists(id='S1')
        self.assertTrue(found)

    def test_not_exists(self):
        found = self.orkg.statements.exists(id='SS1')
        self.assertFalse(found)

    def test_delete(self):
        subject = self.orkg.resources.add(label="ORKG Subject 1").content['id']
        predicate = self.orkg.predicates.add(label="ORKG Predicate 1").content['id']
        object = self.orkg.literals.add(label="ORKG Object 1").content['id']
        res = self.orkg.statements.add(subject_id=subject, predicate_id=predicate, object_id=object)
        st_id = res.content['id']
        self.assertTrue(res.succeeded)
        res = self.orkg.statements.delete(id=st_id)
        self.assertTrue(res.succeeded)
        found = self.orkg.statements.exists(id=st_id)
        self.assertFalse(found)
