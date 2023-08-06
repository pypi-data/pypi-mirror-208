from unittest import TestCase
from orkg import ORKG, OID


class TestTemplates(TestCase):
    """
    Some test scenarios might need to be adjusted to the content of the running ORKG instance
    """
    orkg = ORKG(host="https://sandbox.orkg.org")

    def test_materialize(self):
        self.orkg.templates.materialize_templates(templates=['R199091', 'R199040'], verbose=False)
        self.assertTrue(True)

    def test_df_template(self):
        from pandas import DataFrame as df
        lst = ['this', 'is', 'fancy']
        lst2 = [4, 2, 5]
        param = df(list(zip(lst, lst2)), columns=['word', 'length'])
        self.orkg.templates.materialize_template(template_id='R199091')
        self.orkg.templates.test_df(label="what!", dataset=(param, 'Fancy Table'), uses_library="pyORKG").pretty_print(format='json-ld')
        self.assertTrue(True)

    def test_optional_param(self):
        self.orkg.templates.materialize_template(template_id='R275249')
        print(self.orkg.templates.optional_param.__doc__)
        self.orkg.templates.optional_param(label="what!", uses="pyORKG")
        self.orkg.templates.optional_param(label="wow!", uses="pyORKG", result="https://google.com")
        self.assertTrue(True)

    def test_recursive_templates(self):
        self.orkg.templates.materialize_template(template_id='R48000')
        print(self.orkg.templates.problem.__doc__)
        self.orkg.templates.problem(
            label="Test 1",
            sub_problem=self.orkg.templates.problem(
                label="Test 2",
                sub_problem=OID("R70197"),
                same_as="https://dumpy.url.again",
                description="This is a nested test"
            ),
            same_as="https://dumpy.url",
            description="This is a test"
        ).pretty_print()
        self.assertTrue(True)

    def test_template_cardinality_checks(self):
        self.orkg.templates.materialize_template(template_id='R48000')
        self.orkg.templates.problem(
            label="Test 2",
            sub_problem=self.orkg.templates.problem(
                 label="Test 2",
                 sub_problem=OID("R70197"),
                 same_as="https://dumpy.url.again",
                 description=["More text also!!"]
             ),
            same_as="https://dumpy.url.again",
            description=["This is a nested test"]
        ).pretty_print()
        self.assertTrue(True)

    def test_template_with_list_values(self):
        self.orkg.templates.materialize_template(template_id='R281240')
        self.orkg.templates.multi_param(
            label="multi_param",
            uses=["pyORKG", "rORKG"],
            description="This is a nested test"
        ).pretty_print()
        self.assertTrue(True)
