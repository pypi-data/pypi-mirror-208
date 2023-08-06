from orkg.utils import NamespacedClient, query_params, dict_to_url_params
from orkg.out import OrkgResponse, OrkgUnpaginatedResponse


class PredicatesClient(NamespacedClient):

    def by_id(self, id) -> OrkgResponse:
        self.client.backend._append_slash = True
        response = self.client.backend.predicates(id).GET()
        return self.client.wrap_response(response)

    @query_params("q", "exact", "page", "size", "sort", "desc")
    def get(self, params=None) -> OrkgResponse:
        self.handle_sort_params(params)
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend.predicates.GET(dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.predicates.GET()
        return self.client.wrap_response(response)

    @query_params("q", "exact", "page", "size", "sort", "desc")
    def get_unpaginated(self, params=None, start_page=0, end_page=-1) -> OrkgUnpaginatedResponse:
        return self._call_pageable(
            self.get,
            args={},
            params=params,
            start_page=start_page,
            end_page=end_page
        )

    @query_params("id", "label")
    def add(self, params=None) -> OrkgResponse:
        if len(params) == 0:
            raise ValueError("at least label must be provided")
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.predicates.POST(json=params, headers=self.auth)
        return self.client.wrap_response(response)

    @query_params("id", "label")
    def find_or_add(self, params=None) -> OrkgResponse:
        if len(params) == 0:
            raise ValueError("at least label should be provided")
        else:
            if "id" in params:
                # check if a predicate with this id is there
                found = self.by_id(params['id'])
                if found.succeeded:
                    return found
            # check if a predicate with this label is there
            found = self.get(q=params['label'], exact=True, size=1)
            if found.succeeded:
                if isinstance(found.content, list) and len(found.content) > 0:
                    found.content = found.content[0]
                    return found
            # None found, what the hell! let's create a new one
            self.client.backend._append_slash = True
            response = self.client.backend.predicates.POST(json=params, headers=self.auth)
        return self.client.wrap_response(response)

    @query_params("label")
    def update(self, id, params=None) -> OrkgResponse:
        if len(params) == 0:
            raise ValueError("label must be provided")
        else:
            if not self.exists(id):
                raise ValueError("the provided id is not in the graph")
            self.client.backend._append_slash = True
            response = self.client.backend.predicates(id).PUT(json=params, headers=self.auth)
        return self.client.wrap_response(response)

    def exists(self, id) -> bool:
        return self.by_id(id).succeeded
