from orkg.utils import NamespacedClient
from orkg.out import OrkgResponse


class ObjectsClient(NamespacedClient):

    def add(self, params=None) -> OrkgResponse:
        """
        Warning: Super-users only should use this endpoint
        Create a new object in the ORKG instance
        :param params: orkg Object
        :return: an OrkgResponse object containing the newly created object resource
        """
        self.client.backend._append_slash = True
        response = self.client.backend.objects.POST(json=params, headers=self.auth)
        return self.client.wrap_response(response)

