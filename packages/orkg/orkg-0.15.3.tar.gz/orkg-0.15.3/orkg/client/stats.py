from orkg.utils import NamespacedClient
from orkg.out import OrkgResponse


class StatsClient(NamespacedClient):

    def get(self) -> OrkgResponse:
        self.client.backend._append_slash = True
        response = self.client.backend.stats.GET()
        return self.client.wrap_response(response)
