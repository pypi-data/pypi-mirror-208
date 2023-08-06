from orkg.utils import NamespacedClient, simcomp_available
from orkg.out import OrkgResponse
from typing import List, Tuple
import pandas as pd
from ast import literal_eval
from urllib.parse import urlparse, parse_qs
from typing import Union, Tuple
from collections import defaultdict


class ContributionsClient(NamespacedClient):

    @simcomp_available
    def similar(self, cont_id: str) -> OrkgResponse:
        self.client.simcomp._append_slash = True
        response = self.client.simcomp.similar(cont_id).GET()
        return self.client.wrap_response(response=response)

    @simcomp_available
    def compare(self, contributions: List[str], response_hash: str = None) -> OrkgResponse:
        self.client.simcomp._append_slash = False
        params = f'?contributions={",".join(contributions)}'
        if response_hash is not None:
            params = f'{params}&response_hash={response_hash}'
        response = self.client.simcomp.compare.GET(params)
        return self.client.wrap_response(response=response)

    def __get_contributions_from_comparison(self, comparison_id: str) -> Tuple[List[str], str, List[str]]:
        resource = self.client.resources.by_id(comparison_id).content
        if 'Comparison' not in resource['classes']:
            raise ValueError("This id is not for a comparison")
        response = self.client.json.get_json(resource_id=comparison_id).content
        query_params = parse_qs(urlparse(response['data']['url']).query)
        return query_params['contributions'][0], query_params['response_hash'][0], query_params['properties'][0].split(',') if 'properties' in query_params else []

    @simcomp_available
    def compare_dataframe(self, contributions: List[str] = None, comparison_id: str = None, like_ui=True,
                          include_meta=False) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]:
        ui_props = []
        if contributions is None and comparison_id is None:
            raise ValueError("either provide the contributions, or the comparison ID")
        response_hash = None
        if comparison_id is not None:
            contributions, response_hash, ui_props = self.__get_contributions_from_comparison(comparison_id)
        response = self.compare(contributions=contributions, response_hash=response_hash)
        if not response.succeeded:
            return pd.DataFrame()
        content = response.content
        contributions_list = content['contributions']
        contribution_ids_and_titles = {
            contribution['id']: f"{contribution['title']}/{contribution['contributionLabel']} ({contribution['id']})"
            for contribution in contributions_list
        }
        columns = [contribution_ids_and_titles[contribution['id']] for
                   contribution in contributions_list]
        properties_list = content['properties']
        property_lookup = {prop['id']: prop['label'] for prop in properties_list}
        # create table view of the data
        data = content['data']
        indices = []
        rows = []
        for prop_id, values in data.items():
            indices.append(property_lookup[prop_id])
            row = []
            for index, value in enumerate(values):
                if not value[0]:
                    row.append('')
                else:
                    if len(value) == 1:
                        try:
                            # Try parse the single value into datatype
                            row.append(literal_eval(value[0]['label']))
                        except (SyntaxError, ValueError):
                            # If it fails, that means it is a string
                            row.append(value[0]['label'])
                    else:
                        cell = []
                        # Rather than parsing it in a list comprehension that might fail
                        # Then the whole list will be typed as strings, we parse it one item at a time
                        for v in value:
                            try:
                                # Try parse each value by itself
                                cell.append(literal_eval(v['label']))
                            except (SyntaxError, ValueError):
                                # If it fails, that means it is a string
                                cell.append(v['label'])
                        row.append(cell)
            rows.append(row)
        # create data frame from pieces
        df = pd.DataFrame(rows, columns=columns, index=indices)
        if like_ui and len(ui_props) > 0:
            # remove props that are not displayed
            df = df.drop([p_lbl for p_id, p_lbl in property_lookup.items() if p_id not in ui_props])
            # order df rows by ui props order
            df = df.reindex([property_lookup[p] for p in ui_props if p in property_lookup])
        if include_meta:
            # author, doi, publication month, publication year, url, research field, venue
            meta_property_ids = ['P27', 'P26', 'P28', 'P29', 'url', 'P30', 'HAS_VENUE']
            paper_set = set([f"{contribution['paperId']}" for contribution in contributions_list])
            comparison_meta_data = {}
            # create table view of the data
            for paper in paper_set:
                paper_meta_dict_of_lists = defaultdict(list)
                paper_statements = self.client.statements.get_by_subject_unpaginated(subject_id=paper)
                for statement in paper_statements.content:
                    if statement['predicate']['id'] in meta_property_ids:
                        pred = statement['predicate']['label']
                        obj = statement['object']['label']
                        paper_meta_dict_of_lists[pred].append(obj)
                # make dict values strings if only one and list of strings if two or more
                paper_meta_data = {k: v.pop() if len(v) == 1 else v for k, v in paper_meta_dict_of_lists.items()}
                paper_meta_data['title'] = statement['subject']['label']
                paper_meta_data['paper id'] = paper
                # get IDs of all contributions from this paper which are included in the comparison
                contribution_ids = [str(contribution['id']) for contribution in contributions_list if
                                    contribution['paperId'] == paper]
                # add paper meta info for each contribution to comparison meta info
                for contribution_id in contribution_ids:
                    column_name = contribution_ids_and_titles[contribution_id]
                    paper_dict = paper_meta_data.copy()
                    comparison_meta_data[column_name] = paper_dict
                    comparison_meta_data[column_name]['contribution id'] = contribution_id
            # Make dataframe with same column order as comparison df and replace missing fields with empty string
            df_meta = pd.DataFrame.from_dict(comparison_meta_data)[columns].fillna('')
            return df, df_meta
        return df
