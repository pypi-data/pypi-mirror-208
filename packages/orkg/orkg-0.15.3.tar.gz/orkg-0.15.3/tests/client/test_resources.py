from unittest import TestCase
from orkg import ORKG
from tempfile import NamedTemporaryFile


class TestResources(TestCase):
    """
    Some test scenarios might need to be adjusted to the content of the running ORKG instance
    """
    orkg = ORKG()

    def test_by_id(self):
        res = self.orkg.resources.by_id('R1')
        self.assertTrue(res.succeeded)

    def test_get(self):
        size = 10
        res = self.orkg.resources.get(size=size)
        self.assertTrue(res.succeeded)
        self.assertEqual(len(res.content), size)

    def test_get_unpaginated(self):
        size = 500
        res = self.orkg.resources.get_unpaginated(size=size, end_page=5)
        self.assertTrue(res.all_succeeded)

    def test_delete(self):
        to_delete = self.orkg.resources.add(label="I should be deleted")
        print(to_delete.content)
        self.assertTrue(to_delete.succeeded)
        res = self.orkg.resources.delete(id=to_delete.content["id"])
        self.assertTrue(res.succeeded)
        self.assertFalse(self.orkg.resources.exists(to_delete.content["id"]))

    def test_add(self):
        label = "test"
        res = self.orkg.resources.add(label=label)
        self.assertTrue(res.succeeded)
        self.assertEqual(res.content['label'], label)

    def test_find_or_add_with_label(self):
        import random
        import string
        label = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(15))
        old = self.orkg.resources.add(label=label)
        self.assertTrue(old.succeeded, 'Creating first resource is a success')
        self.assertEqual(old.content['label'], label, 'The first resource has the correct label')
        new = self.orkg.resources.find_or_add(label=label)
        self.assertTrue(new.succeeded, 'Creating second resource is a success')
        self.assertEqual(new.content['id'], old.content['id'], 'the two resources have the same id')

    def test_find_or_add_with_label_and_class(self):
        import random
        import string
        label = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(15))
        lst_of_classes = self.orkg.classes.get_all()
        class_id = lst_of_classes.content[0]['id']
        old = self.orkg.resources.add(label=label, classes=[class_id])
        self.assertTrue(old.succeeded, 'Creating first resource is a success')
        self.assertEqual(old.content['label'], label, 'The first resource has the correct label')
        self.assertEqual(old.content['classes'], [class_id], 'The first resource has the correct class')
        new = self.orkg.resources.find_or_add(label=label, classes=[class_id])
        self.assertTrue(new.succeeded, 'Creating second resource is a success')
        self.assertEqual(new.content['id'], old.content['id'], 'the two resources have the same id')

    def test_add_with_class(self):
        label = "test"
        cls = "Coco"
        res = self.orkg.resources.add(label=label, classes=[cls])
        self.assertTrue(res.succeeded)
        self.assertEqual(res.content['label'], label)
        self.assertIn(cls, res.content['classes'])

    def test_update(self):
        res = self.orkg.resources.add(label="Coco")
        self.assertTrue(res.succeeded)
        label = "test"
        res = self.orkg.resources.update(id=res.content['id'], label=label)
        self.assertTrue(res.succeeded)
        res = self.orkg.resources.by_id(res.content['id'])
        self.assertTrue(res.succeeded)
        self.assertEqual(res.content['label'], label)

    def test_add_tabular_data(self):
        csv_content = """Statistics,Event start time,Event end time,Duration,Sunrise,Sunset
Min,09:05,14:25,04:41,04:34,16:29
Max,12:17,18:41,06:32,07:50,19:53
Mean,10:58,16:46,05:47,06:13,18:12
Median,11:07,16:51,05:43,06:15,18:14
"""
        label = "test dataset XXI"

        csv_file = NamedTemporaryFile(mode="w", delete=False)
        csv_file.write(csv_content)
        csv_path = csv_file.name
        csv_file.close()

        res = self.orkg.resources.save_dataset(
            csv_path, label,
            ["Statistics", "Event start time", "Event end time", "Duration", "Sunrise", "Sunset"]
        )

        self.assertTrue(res.succeeded)
        self.assertEqual(res.content['label'], label)
