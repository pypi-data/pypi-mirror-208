from orkg.utils import NamespacedClient, query_params, dict_to_url_params, admin_functionality
from orkg.out import OrkgResponse, OrkgUnpaginatedResponse
from pandas import read_csv
import os


class ResourcesClient(NamespacedClient):

    def by_id(self, id) -> OrkgResponse:
        """
        Lookup a resource by id
        :param id: the id of the resource to lookup
        :return: an OrkgResponse object containing the resource
        """
        self.client.backend._append_slash = True
        response = self.client.backend.resources(id).GET()
        return self.client.wrap_response(response)

    @query_params("q", "exact", "page", "size", "sort", "desc", "exclude")
    def get(self, params=None) -> OrkgResponse:
        """
        Fetch a list of resources, with the possibility to paginate the results and filter them out based on label
        :param q: search term of the label of the resource (optional)
        :param exact: whether to check for the exact search term or not (optional) -> bool
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :param exclude: classes to be excluded in search (optional)
        :return: an OrkgResponse object contains the list of resources
        """
        self.handle_sort_params(params)
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend.resources.GET(dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.resources.GET()
        return self.client.wrap_response(response)

    @query_params("q", "exact", "page", "size", "sort", "desc", "exclude")
    def get_unpaginated(self, params=None, start_page=0, end_page=-1) -> OrkgUnpaginatedResponse:
        """
        Fetch all resources returned by all pages between start_page and end_page.

        :param q: search term of the label of the resource (optional)
        :param exact: whether to check for the exact search term or not (optional) -> bool
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :param exclude: classes to be excluded in search (optional)
        :param start_page: page to start from. Defaults to 0 (optional)
        :param end_page: page to stop at. Defaults to -1 meaning non-stop (optional)
        :return: an OrkgUnpaginatedResponse object
        """
        return self._call_pageable(
            self.get,
            args={},
            params=params,
            start_page=start_page,
            end_page=end_page
        )

    @query_params("id", "label", "classes")
    def add(self, params=None) -> OrkgResponse:
        """
        Create a new resource in the ORKG instance
        :param id: the specific id to add (optional)
        :param label: the label of the new resource (optional)
        :param classes: list of classes to assign the resource to (optional)
        :return: an OrkgResponse object containing the newly created resource
        """
        if len(params) == 0:
            raise ValueError("at least label should be provided")
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.resources.POST(json=params, headers=self.auth)
        return self.client.wrap_response(response)

    @query_params("id", "label", "classes")
    def find_or_add(self, params=None) -> OrkgResponse:
        """
        find or create a new resource in the ORKG instance
        :param id: the specific id to add (optional)
        :param label: the label of the new resource (optional)
        :param classes: list of classes to assign the resource to (optional)
        :return: an OrkgResponse object containing the found or newly created resource
        """
        if len(params) == 0:
            raise ValueError("at least a label should be provided")
        else:
            if "id" in params:
                # check if a resource with this id is there
                found = self.by_id(params['id'])
                if found.succeeded:
                    return found
            if "label" in params and "classes" in params:
                class_id = params['classes'][0]
                # check if a resource exists with this label and the _first_ class from params class list
                found = self.client.classes.get_resource_by_class(class_id, q=params['label'], exact=True, size=1)
                if found.succeeded:
                    if isinstance(found.content, list) and len(found.content) > 0:
                        found.content = found.content[0]
                        return found
            # if no class is passed, check if a resource with this label is there
            elif "label" in params:
                found = self.get(q=params['label'], exact=True, size=1)
                if found.succeeded:
                    if isinstance(found.content, list) and len(found.content) > 0:
                        found.content = found.content[0]
                        return found
            # None found, what the hell! let's create a new one
            self.client.backend._append_slash = True
            response = self.client.backend.resources.POST(json=params, headers=self.auth)
        return self.client.wrap_response(response)

    @query_params("label", "classes")
    def update(self, id, params=None) -> OrkgResponse:
        """
        Update a resource with a specific id
        :param id: the id of the resource to update
        :param label: the new label (optional)
        :param classes: the updated list of classes (optional)
        :return: an OrkgResponse object contains the newly updated resource
        """
        if len(params) == 0:
            raise ValueError("at least label should be provided")
        else:
            if not self.exists(id):
                raise ValueError("the provided id is not in the graph")
            self.client.backend._append_slash = True
            response = self.client.backend.resources(id).PUT(json=params, headers=self.auth)
        return self.client.wrap_response(response)

    @admin_functionality
    def update_observatory(self, id: str, observatory_id: str, organization_id: str) -> OrkgResponse:
        """
        Update the observatory and the organization of a particular resource
        NOTE: this is a call only for admins
        :param id: The id of the resource to update
        :param observatory_id: the new observatory id
        :param organization_id: the new organization id
        :return: an OrkgResponse object contains the newly updated resource
        """
        if not self.exists(id):
            raise ValueError("the provided id is not in the graph")
        self.client.backend._append_slash = False
        content = {
            'observatory_id': observatory_id,
            'organization_id': organization_id
        }
        response = self.client.backend.resources(id).observatory.PUT(json=content, headers=self.auth)
        return self.client.wrap_response(response)

    def exists(self, id) -> bool:
        """
        Check if a resource exists in the graph
        :param id: the id of the resource to check
        :return: true if found, otherwise false
        """
        return self.by_id(id).succeeded

    @admin_functionality
    def delete(self, id) -> OrkgResponse:
        if not self.exists(id):
            raise ValueError("the provided id is not in the graph")
        self.client.backend._append_slash = True
        response = self.client.backend.resources(id).DELETE(headers=self.auth)
        return self.client.wrap_response(response)

    def save_dataset(self, file, label, dimensions) -> OrkgResponse:
        """
        Create a resource of a tabular data using RDF Datacube vocabulary starting from a CSV file
        :param file: CSV file containing the table
        :param label: label of the resource
        :param dimensions: a list of column(s) name(s) that represent the dimensions.
        :return: the resource ID of the dataset
        """
        
        if not file:
            raise ValueError("the file should be provided")
        if not label:
            raise ValueError("the label should be provided")

        if not os.path.exists(file):
            raise ValueError(f"file path doesn't exist!, path={file}")
                                
        dataset = read_csv(file, dtype=str)                      
        # Vocabulary Classes
        cQB_DATASET_CLASS = self.client.classes.find_or_add(id="QBDataset", label="qb:DataSet").content['id']
        cDataStructureDefinition = self.client.classes.find_or_add(label="qb:DataStructureDefinition").content['id']
        cComponentSpecification = self.client.classes.find_or_add(label="qb:ComponentSpecification").content['id']
        cComponentProperty = self.client.classes.find_or_add(label="qb:ComponentProperty").content['id']
        cDimensionProperty = self.client.classes.find_or_add(label="qb:DimensionProperty").content['id']
        cMeasureProperty = self.client.classes.find_or_add(label="qb:MeasureProperty").content['id']
        cObservation = self.client.classes.find_or_add(label="qb:Observation").content['id']
        # Vocabulary Predicates
        pStructure = self.client.predicates.find_or_add(label="structure").content['id']
        pComponent = self.client.predicates.find_or_add(label="component").content['id']
        pDimension = self.client.predicates.find_or_add(label="dimension").content['id']
        pMeasure = self.client.predicates.find_or_add(label="measure").content['id']
        pDataSet = self.client.predicates.find_or_add(label="dataSet").content['id']
        pOrder = self.client.predicates.find_or_add(label="order").content['id']
        # Create dataset resource
        rds = self.client.resources.add(label=label, classes=[cQB_DATASET_CLASS])
        rds_id = rds.content['id']
        # Create Data Structure Definition
        rDsd = self.client.resources.add(label="Data Structure Definition", classes=[cDataStructureDefinition]).content['id']
        self.client.statements.add(subject_id=rds_id, predicate_id=pStructure, object_id=rDsd)
        # Schema Definition
        cs = dict()  # component specifications
        dt = dict()  # component properties
        dtP = dict()  # resources used in the predicate position
        for index, column in enumerate(dataset.columns, start=1):
            cs[column] = self.client.resources.add(label="Component Specification " + column, classes=[cComponentSpecification]).content['id']
            self.client.statements.add(subject_id=rDsd, predicate_id=pComponent, object_id=cs[column])
            # Order
            lOrder = self.client.literals.add(label=str(index)).content['id']
            self.client.statements.add(subject_id=cs[column], predicate_id=pOrder, object_id=lOrder)
            if column in dimensions:
                dt[column] = self.client.resources.add(label=column, classes=[cComponentProperty, cDimensionProperty]).content['id']
                self.client.statements.add(subject_id=cs[column], predicate_id=pDimension, object_id=dt[column])
            else:
                dt[column] = self.client.resources.add(label=column, classes=[cComponentProperty, cMeasureProperty]).content['id']
                self.client.statements.add(subject_id=cs[column], predicate_id=pMeasure, object_id=dt[column])
            # Name a predicate with the resource ID
            dtP[column] = self.client.predicates.find_or_add(label=dt[column]).content['id']
            
        # Observations
        for index, row in dataset.iterrows():
            ro = self.client.resources.add(label='Observation #{}'.format(index+1), classes=[cObservation]).content['id']
            self.client.statements.add(subject_id=ro, predicate_id=pDataSet, object_id=rds_id)
            # set the values
            for column in dataset.columns:
                lid = self.client.literals.add(label=str(row[column])).content['id']
                self.client.statements.add(subject_id=ro, predicate_id=dtP[column], object_id=lid)
        return rds

