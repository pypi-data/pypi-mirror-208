from orkg.utils import NamespacedClient, query_params
from orkg.out import OrkgResponse
from pandas import read_csv
import re
from ast import literal_eval
import os


class PapersClient(NamespacedClient):

    def add(self, params=None, merge_if_exists=False) -> OrkgResponse:
        """
        Create a new paper in the ORKG instance
        :param params: paper Object
        :param merge_if_exists: merge the papers if they exist in the graph and append contributions
        :return: an OrkgResponse object containing the newly created paper resource
        """
        self.client.backend._append_slash = True
        response = self.client.backend.papers.POST(json=params, params={'mergeIfExists': merge_if_exists}, headers=self.auth)
        return self.client.wrap_response(response)

    @query_params("file", "standard_statements")
    def add_csv(self, params=None) -> OrkgResponse:
        """
        Create a new paper in the ORKG instance
        :param file: csv file containing the papers, with at least a column with title: "paper:title"
        :param standard_statements: dict with default statements, should contain CSV_PLACEHOLDER (optional)
        :return: an list with paper ids and contribution ids 
        """
        if 'file' not in params:
            return
        if not os.path.exists(params['file']):
            raise ValueError(f"file path doesn't exist!, path={params['file']}")

        df = read_csv(params['file'], dtype=str)
        contribution_ids = []

        for index in range(len(df)):
            paper = df.iloc[index].to_dict()

            # at least a paper title should be present
            if 'paper:title' not in paper: # TODO: enable crossref lookup based on DOI
                print('Skipping paper, column "paper:title" not found')
                continue

            # check for paper metadata
            title = paper['paper:title']
            authors = [{'label': author.strip()} for author in str(paper['paper:authors']).split(';')] if 'paper:authors' in paper and paper['paper:authors'] == paper['paper:authors'] else []
            publication_month = self.__setValue('paper:publication_month', paper, 1)
            publication_year = self.__setValue('paper:publication_year', paper, 2000)
            research_field = self.__setValue('paper:research_field', paper, 'R11')
            doi = self.__setValue('paper:doi', paper, '')
            url = ''
            published_in = ''
            standard_statements = literal_eval(
                params['standard_statements']) if 'standard_statements' in params else {}
            contribution_statements = {}

            # remove metadata from paper dict, already added above
            metadata_headers = ['paper:title', 'paper:authors', 'paper:publication_month', 'paper:publication_year', 'paper:doi', 'paper:research_field']
            [paper.pop(key) if key in paper else paper for key in metadata_headers] 

            research_problems = []    
            # generate the statements based on the remaining columns
            for predicate in paper:
                value = paper[predicate]

                # add research problem (one or more)
                if (predicate.startswith('contribution:research_problem')):
                    research_problem = self.__setValue(predicate, paper, '')

                    if (research_problem != ''):
                        research_problems.append(research_problem)

                    continue


                # filter out nan values
                if value != value:
                    continue
                
                predicate = re.sub('\.[1-9]+$', '', predicate) # to make columns unique, pandas appends a dot and number to duplicate columns, remove this here
                
                value_is_resource = False

                # if predicate starts with resource:, insert it as resource instead of literal
                if predicate.startswith('resource:'):
                    value_is_resource = True
                    predicate = predicate[len('resource:'):]

                predicate_id = self.client.predicates.find_or_add(label=predicate).content['id']

                if not value_is_resource:
                    if predicate_id in contribution_statements:
                        contribution_statements[predicate_id].append({'text': value})
                    else:
                        contribution_statements[predicate_id] = [
                            {'text': value}
                        ]
                else:
                    resource_id = self.client.resources.find_or_add(label=value).content['id']
                    if predicate_id in contribution_statements:
                        contribution_statements[predicate_id].append({'@id': resource_id})
                    else:
                        contribution_statements[predicate_id] = [
                            {'@id': resource_id}
                        ]

            # add default statements if they are present 
            # TODO: only works for one level now, make it recursive
            statements_to_insert = standard_statements.copy()

            if len(statements_to_insert) > 0:
                for predicate in statements_to_insert:
                    if isinstance(statements_to_insert[predicate], list):  # if is array
                        for i in range(len(statements_to_insert[predicate])):
                            if statements_to_insert[predicate][i]['values'] == 'CSV_PLACEHOLDER':
                                statements_to_insert[predicate][i]['values'] = contribution_statements

                    if not re.search("^[P]+[a-zA-Z0-9]*$", predicate):
                        predicate_id = self.client.predicates.find_or_add(label=predicate).content['id']
                        statements_to_insert[predicate_id] = statements_to_insert[predicate]
                        del statements_to_insert[predicate]

                contribution_statements = statements_to_insert

            # add research problem to the contribution 
            if len(research_problems) > 0:
                contribution_statements['P32'] = []
                
                for research_problem in research_problems:
                    research_problem_id = \
                        self.client.resources.find_or_add(label=research_problem, classes=['Problem']).content['id']

                    # P32 has research problem 
                    contribution_statements['P32'].append({'@id': research_problem_id})

            # check if a paper with this title already exists 
            existing_papers = self.client.resources.get(q=title, exact=True).content
            existing_paper_id = 0

            for existing_paper in existing_papers:
                if 'Paper' in existing_paper['classes']:
                    existing_paper_id = existing_paper['id']
                    break

            # paper does not yet exist
            if existing_paper_id == 0:
                paper = {
                    'paper': {
                        'title': title,
                        'authors': authors,
                        'publicationMonth': publication_month,
                        'publicationYear': publication_year,
                        'researchField': research_field,
                        'doi': doi,
                        'url': url,
                        'publishedIn': published_in,
                        'contributions': [{
                            'name': 'Contribution 1',
                            'values': contribution_statements
                        }]
                    }
                }
                response = self.add(paper)

                if 'id' in response.content:
                    paper_id = response.content['id']
                    paper_statements = self.client.statements.get_by_subject(subject_id=paper_id, size=10000).content
                    for statement in paper_statements:
                        if statement['predicate']['id'] == 'P31':
                            contribution_ids.append(statement['object']['id'])
                            print('Added paper:', str(paper_id))
                else:
                    print('Error adding paper: ', str(response.content))

            # paper exists already, so add a contribution       
            else:
                paper_statements = self.client.statements.get_by_subject(subject_id=existing_paper_id, size=10000).content
                contribution_amount = 0

                for paper_statement in paper_statements:
                    if paper_statement['predicate']['id'] == 'P31':
                        contribution_amount += 1

                contribution_id = self.client.resources.add(label='Contribution ' + str(contribution_amount + 1),
                                                            classes=['Contribution']).content['id']

                self.client.statements.add(subject_id=existing_paper_id, predicate_id='P31', object_id=contribution_id)
                self.__create_statements(contribution_id, contribution_statements)

                contribution_ids.append(contribution_id)

                print('Added contribution:', str(contribution_id), 'to paper:', str(existing_paper_id))

        return self.client.wrap_response(content=contribution_ids, status_code="201")
    
    # function to check if key exists and value is not NaN
    def __setValue(self, key, dict, defaultValue):
        return dict[key] if key in dict and dict[key] == dict[key] else defaultValue

    def __create_statements(self, subject_id, statements):
        for predicate_id in statements:
            values = statements[predicate_id]

            for value in values:
                if 'text' in value:
                    literal_id = self.client.literals.add(label=value['text']).content['id']
                    self.client.statements.add(subject_id=subject_id, predicate_id=predicate_id, object_id=literal_id)
                elif '@id' in value:
                    self.client.statements.add(subject_id=subject_id, predicate_id=predicate_id, object_id=value['@id'])
                elif 'label' in value:
                    resource_id = self.client.resources.add(label=value['label']).content['id']
                    self.client.statements.add(subject_id=subject_id, predicate_id=predicate_id, object_id=resource_id)
                    self.__create_statements(resource_id, value['values'])
