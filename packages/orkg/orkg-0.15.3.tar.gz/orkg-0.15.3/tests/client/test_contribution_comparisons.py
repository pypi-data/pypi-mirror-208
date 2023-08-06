from unittest import TestCase

from orkg import ORKG


class TestContributionComparisons(TestCase):
    """
    Some test scenarios might need to be adjusted to the content of the running ORKG instance
    """
    orkg = ORKG()

    def test_by_ids(self):
        res = self.orkg.contribution_comparisons.by_ids(ids=["R166186", "R166180"])
        self.assertTrue(res.succeeded)

    def test_by_ids_unpaginated(self):
        size = 10
        res = self.orkg.contribution_comparisons.by_ids_unpaginated(
            ids=["R166186", "R166180"] * size, size=size, end_page=5
        )
        self.assertTrue(res.all_succeeded)
