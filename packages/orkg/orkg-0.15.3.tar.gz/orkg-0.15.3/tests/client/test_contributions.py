from unittest import TestCase
from orkg import ORKG
import pandas as pd


class TestContributions(TestCase):
    """
    Some test scenarios might need to be adjusted to the content of the running ORKG instance
    """
    orkg = ORKG()

    def test_check_simcomp(self):
        self.assertTrue(self.orkg.simcomp_available)

    def test_get_similar(self):
        res = self.orkg.contributions.similar('R3005')
        self.assertTrue(res.succeeded)

    def test_get_comparison(self):
        res = self.orkg.contributions.compare(['R3005', 'R1010'])
        self.assertTrue(res.succeeded)

    def test_get_comparison_df_without_metadata(self):
        res = self.orkg.contributions.compare_dataframe(contributions=['R34499', 'R34504'])

    def test_get_comparison_df_on_comparison_without_metadata(self):
        res = self.orkg.contributions.compare_dataframe(comparison_id='R41466')

    def test_get_comparison_df_with_metadata(self):
        res = self.orkg.contributions.compare_dataframe(contributions=['R34499', 'R34504'])
        self.assertIsInstance(res, pd.DataFrame)
        res = self.orkg.contributions.compare_dataframe(contributions=['R34499', 'R34504'], include_meta=True)
        self.assertIsInstance(res, tuple)
        self.assertTrue((res[0].columns == res[1].columns).all())
        self.assertTrue('paper id' in res[1].index and 'contribution id' in res[1].index)
        self.assertTrue(res[1].loc['contribution id'].is_unique)

    def test_get_comparison_df_on_comparison_with_metadata(self):
        res = self.orkg.contributions.compare_dataframe(comparison_id='R41466')
        self.assertIsInstance(res, pd.DataFrame)
        res = self.orkg.contributions.compare_dataframe(comparison_id='R41466', include_meta=True)
        self.assertIsInstance(res, tuple)
        self.assertTrue((res[0].columns == res[1].columns).all())
        self.assertTrue('paper id' in res[1].index and 'contribution id' in res[1].index)
        self.assertTrue(res[1].loc['contribution id'].is_unique)