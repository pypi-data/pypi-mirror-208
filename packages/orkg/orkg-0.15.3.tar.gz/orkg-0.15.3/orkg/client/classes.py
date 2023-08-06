from orkg.utils import NamespacedClient, query_params, dict_to_url_params
from orkg.out import OrkgResponse, OrkgUnpaginatedResponse


class ClassesClient(NamespacedClient):

    def by_id(self, id):
        self.client.backend._append_slash = True
        response = self.client.backend.classes(id).GET()
        return self.client.wrap_response(response)

    @query_params("q", "exact")
    def get_all(self, params=None) -> OrkgResponse:
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend.classes.GET(dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.classes.GET()
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc", "q", "exact")
    def get_resource_by_class(self, class_id, params=None) -> OrkgResponse:
        self.handle_sort_params(params)
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend.classes(class_id).resources.GET(dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.classes(class_id).resources.GET()
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc", "q", "exact")
    def get_resource_by_class_unpaginated(
            self,
            class_id,
            params=None,
            start_page=0,
            end_page=-1
    ) -> OrkgUnpaginatedResponse:
        return self._call_pageable(
            self.get_resource_by_class,
            args={
                'class_id': class_id
            },
            params=params,
            start_page=start_page,
            end_page=end_page
        )

    @query_params("id", "label", "uri")
    def add(self, params=None) -> OrkgResponse:
        if len(params) == 0:
            raise ValueError("at least label should be provided")
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.classes.POST(json=params, headers=self.auth)
        return self.client.wrap_response(response)

    @query_params("id", "label", "uri")
    def find_or_add(self, params=None) -> OrkgResponse:
        if len(params) == 0:
            raise ValueError("at least label should be provided")
        else:
            if "id" in params:
                # check if a class with this id is there
                found = self.by_id(params['id'])
                if found.succeeded:
                    return found
            # check if a class with this label is there
            found = self.get_all(q=params['label'], exact=True)
            if found.succeeded:
                if isinstance(found.content, list) and len(found.content) > 0:
                    found.content = found.content[0]
                    return found
            # None found! let's create a new one
            self.client.backend._append_slash = True
            response = self.client.backend.classes.POST(json=params, headers=self.auth)
        return self.client.wrap_response(response)

    @query_params("label", "uri")
    def update(self, id, params=None) -> OrkgResponse:
        if len(params) == 0:
            raise ValueError("at least label should be provided")
        else:
            if not self.exists(id):
                raise ValueError("the provided id is not in the graph")
            self.client.backend._append_slash = True
            response = self.client.backend.classes(id).PUT(json=params, headers=self.auth)
        return self.client.wrap_response(response)

    def exists(self, id) -> bool:
        return self.by_id(id).succeeded

