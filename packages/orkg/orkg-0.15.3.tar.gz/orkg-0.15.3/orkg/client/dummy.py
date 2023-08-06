from orkg.utils import NamespacedClient
from orkg.out import OrkgResponse
from typing import Dict, List, Union


class DummyClient(NamespacedClient):

    def create_xxx_response(self, code: str, content: Union[Dict, List]) -> OrkgResponse:
        return OrkgResponse(status_code=code, content=content, paged=False, response=None, url="")

    def create_200_response(self, content: Union[Dict, List]) -> OrkgResponse:
        return self.create_xxx_response("200", content)

    def create_404_response(self, content: Union[Dict, List]) -> OrkgResponse:
        return self.create_xxx_response("404", content)
