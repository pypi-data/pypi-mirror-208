from unittest import TestCase

import networkx as nx

import orkg


class TestGraph(TestCase):
    """
    Some test scenarios might need to be adjusted to the content of the running ORKG instance
    """
    client = orkg.ORKG(host='https://incubating.orkg.org/')

    def test_subgraph(self):
        statements, contribution, adj = self._create_contribution()

        subgraph = orkg.subgraph(self.client, contribution)
        self.assertIsInstance(subgraph, nx.DiGraph)

        self.assertEqual(4, len(subgraph.nodes))
        self.assertEqual(3, len(subgraph.edges))

        for statement in statements:
            start_node = subgraph.nodes[statement.content['subject']['id']]
            start_label = statement.content['subject']['label']
            self.assertEqual(start_node['label'], start_label)

            target_node = subgraph.nodes[statement.content['object']['id']]
            target_label = statement.content['object']['label']
            self.assertEqual(target_node['label'], target_label)

            edge = subgraph.edges[start_node['id'], target_node['id']]
            edge_label = statement.content['predicate']['label']
            self.assertEqual(edge['label'], edge_label)

        self._delete_subgraph(statements)

    def _delete_subgraph(self, statements):
        for statement in statements:
            res = self.client.statements.delete(id=statement.content['id'])
            self.assertTrue(res.succeeded)

    def _create_contribution(self):
        """
        Contribution -> predicate_1 -> label_1;
                        predicate_2 -> object_1 .
        object_1 -> predicate_3 -> label_2
        """
        contribution = self.client.resources.add(label="Contribution").content['id']
        predicate_1 = self.client.predicates.add(label="predicate_1").content['id']
        label_1 = self.client.literals.add(label="label_1").content['id']
        statement_1 = self.client.statements.add(subject_id=contribution, predicate_id=predicate_1, object_id=label_1)

        predicate_2 = self.client.predicates.add(label="predicate_2").content['id']
        object_1 = self.client.resources.add(label="object_1").content['id']
        statement_2 = self.client.statements.add(subject_id=contribution, predicate_id=predicate_2, object_id=object_1)

        predicate_3 = self.client.predicates.add(label="predicate_3").content['id']
        label_2 = self.client.literals.add(label="label_2").content['id']
        statement_3 = self.client.statements.add(subject_id=object_1, predicate_id=predicate_3, object_id=label_2)

        adj = {contribution: {label_1: predicate_1, object_1: predicate_2}, object_1: {label_2: predicate_3}}
        return [statement_1, statement_2, statement_3], contribution, adj


