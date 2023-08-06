from orkg.utils import NamespacedClient, query_params, dict_to_url_params
from orkg.out import OrkgResponse, OrkgUnpaginatedResponse


class StatementsClient(NamespacedClient):

    def by_id(self, id) -> OrkgResponse:
        self.client.backend._append_slash = True
        response = self.client.backend.statements(id).GET()
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get(self, params=None) -> OrkgResponse:
        self.handle_sort_params(params)
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend.statements.GET(dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.statements.GET()
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_unpaginated(self, params=None, start_page=0, end_page=-1) -> OrkgUnpaginatedResponse:
        return self._call_pageable(
            self.get,
            args={},
            params=params,
            start_page=start_page,
            end_page=end_page
        )

    @query_params("page", "size", "sort", "desc")
    def get_by_subject(self, subject_id, params=None) -> OrkgResponse:
        self.handle_sort_params(params)
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend.statements.subject(subject_id).GET(dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.statements.subject(subject_id).GET()
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_by_subject_unpaginated(self, subject_id, params=None, start_page=0, end_page=-1) -> OrkgUnpaginatedResponse:
        return self._call_pageable(
            self.get_by_subject,
            args={
                'subject_id': subject_id
            },
            params=params,
            start_page=start_page,
            end_page=end_page
        )

    @query_params("page", "size", "sort", "desc")
    def get_by_predicate(self, predicate_id, params=None) -> OrkgResponse:
        self.handle_sort_params(params)
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend.statements.predicate(predicate_id).GET(dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.statements.predicate(predicate_id).GET()
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_by_predicate_unpaginated(
            self,
            predicate_id,
            params=None,
            start_page=0,
            end_page=-1
    ) -> OrkgUnpaginatedResponse:
        return self._call_pageable(
            self.get_by_predicate,
            args={
                'predicate_id': predicate_id
            },
            params=params,
            start_page=start_page,
            end_page=end_page
        )

    @query_params("page", "size", "sort", "desc")
    def get_by_object(self, object_id, params=None) -> OrkgResponse:
        self.handle_sort_params(params)
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend.statements.object(object_id).GET(dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.statements.object(object_id).GET()
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_by_object_unpaginated(self, object_id, params=None, start_page=0, end_page=-1) -> OrkgUnpaginatedResponse:
        return self._call_pageable(
            self.get_by_object,
            args={
                'object_id': object_id
            },
            params=params,
            start_page=start_page,
            end_page=end_page
        )

    @query_params("page", "size", "sort", "desc")
    def get_by_object_and_predicate(self, object_id, predicate_id, params=None) -> OrkgResponse:
        self.handle_sort_params(params)
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend.statements.object(object_id).predicate(predicate_id).GET(dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.statements.object(object_id).predicate(predicate_id).GET()
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_by_object_and_predicate_unpaginated(
            self,
            object_id,
            predicate_id,
            params=None,
            start_page=0,
            end_page=-1
    ) -> OrkgUnpaginatedResponse:
        return self._call_pageable(
            self.get_by_object_and_predicate,
            args={
                'object_id': object_id,
                'predicate_id': predicate_id
            },
            params=params,
            start_page=start_page,
            end_page=end_page
        )

    @query_params("page", "size", "sort", "desc")
    def get_by_subject_and_predicate(self, subject_id, predicate_id, params=None) -> OrkgResponse:
        self.handle_sort_params(params)
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend.statements.subject(subject_id).predicate(predicate_id).GET(
                dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.statements.subject(subject_id).predicate(predicate_id).GET()
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_by_subject_and_predicate_unpaginated(
            self,
            subject_id,
            predicate_id,
            params=None,
            start_page=0,
            end_page=-1
    ) -> OrkgUnpaginatedResponse:
        return self._call_pageable(
            self.get_by_subject_and_predicate,
            args={
                'subject_id': subject_id,
                'predicate_id': predicate_id
            },
            params=params,
            start_page=start_page,
            end_page=end_page
        )

    @query_params("subject_id", "predicate_id", "object_id")
    def add(self, params=None) -> OrkgResponse:
        if len(params) != 3:
            raise ValueError("all parameters must be provided")
        else:
            self.client.backend._append_slash = True
            params['object'] = {'id': params['object_id'], '_class': 'literal' if params['object_id'][0] == 'L' else 'resource'}
            response = self.client.backend.statements.POST(json=params, headers=self.auth)
        return self.client.wrap_response(response)

    @query_params("subject_id", "predicate_id", "object_id")
    def update(self, id, params=None) -> OrkgResponse:
        if len(params) == 0:
            raise ValueError("at least one parameter must be provided")
        else:
            if not self.exists(id):
                raise ValueError("the provided id is not in the graph")
            self.client.backend._append_slash = True
            response = self.client.backend.statements(id).PUT(json=params, headers=self.auth)
        return self.client.wrap_response(response)

    @query_params("minLevel", "maxLevel", "blacklist", "whitelist", "includeFirst")
    def bundle(self, thing_id, params=None) -> OrkgResponse:
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend.statements(thing_id).bundle.GET(dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.statements(thing_id).bundle.GET()

        return self.client.wrap_response(response)

    def delete(self, id) -> OrkgResponse:
        if not self.exists(id):
            raise ValueError("the provided id is not in the graph")
        self.client.backend._append_slash = True
        response = self.client.backend.statements(id).DELETE()
        return self.client.wrap_response(response)

    def exists(self, id) -> bool:
        return self.by_id(id).succeeded
