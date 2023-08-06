from unittest import TestCase
from orkg import ORKG
from tempfile import NamedTemporaryFile


class TestObjects(TestCase):
    """
    Some test scenarios might need to be adjusted to the content of the running ORKG instance
    """
    orkg = ORKG()

    def test_add(self):
        obj = {
            "predicates": [],
            "resource": {
                "name": "I rock maybe!",
                "classes": [
                    "C2000"
                ],
                "values": {
                    "P32": [
                        {
                            "@id": "R2"
                        }
                    ],
                    "P55": [
                        {
                            "label": "ORKG is so cool!",
                            "classes": [
                                "C3000"
                            ]
                        }
                    ]
                }
            }
        }
        res = self.orkg.objects.add(params=obj)
        self.assertTrue(res.succeeded)
