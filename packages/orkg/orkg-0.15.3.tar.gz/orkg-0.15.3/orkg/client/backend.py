import hammock

from .contribution_comparisons import ContributionComparisonsClient
from .resources import ResourcesClient
from .predicates import PredicatesClient
from .classes import ClassesClient
from .literals import LiteralsClient
from .stats import StatsClient
from .statements import StatementsClient
from .papers import PapersClient
from .comparisons import ComparisonsClient
from .contributions import ContributionsClient
from .objects import ObjectsClient
from .dummy import DummyClient
from .json import JSONClient
from .templates import TemplatesClient
from orkg.out import OrkgResponse
from typing import Union


class ORKG(object):

    def __init__(self, host=None, simcomp_host=None, creds=None, **kwargs):
        if host is not None and not host.startswith('http'):
            raise ValueError('host must begin with http or https')
        self.host = host if host is not None else 'http://127.0.0.1:8080'
        if self.host[-1] == '/':
            self.host = self.host[:-1]
        if simcomp_host is not None and not simcomp_host.startswith('http'):
            raise ValueError('simcomp host must begin with http or https')
        self.simcomp_host = simcomp_host
        self.core = hammock.Hammock(self.host)
        if self.simcomp_available:
            self.simcomp = hammock.Hammock(self.simcomp_host)
        self.token = None
        if creds is not None and len(creds) == 2:
            self.__authenticate(creds[0], creds[1])
        self.backend = self.core.api
        self.resources = ResourcesClient(self)
        self.predicates = PredicatesClient(self)
        self.classes = ClassesClient(self)
        self.literals = LiteralsClient(self)
        self.stats = StatsClient(self)
        self.statements = StatementsClient(self)
        self.papers = PapersClient(self)
        self.comparisons = ComparisonsClient(self)
        self.contributions = ContributionsClient(self)
        self.objects = ObjectsClient(self)
        self.dummy = DummyClient(self)
        self.json = JSONClient(self)
        self.templates = TemplatesClient(self)
        self.contribution_comparisons = ContributionComparisonsClient(self)

    @property
    def simcomp_available(self):
        return self.simcomp_host is not None

    def __authenticate(self, email, password):
        data = {
            'username': email,
            'grant_type': 'password',
            'client_id': 'orkg-client',
            'password': password
        }
        resp = self.core.oauth.token.POST(data=data, headers={'Authorization': 'Basic b3JrZy1jbGllbnQ6c2VjcmV0'})
        if resp.status_code == 200:
            self.token = resp.json()['access_token']
        else:
            raise IOError(f"Please check the credentials provided!, got the error {resp.content}")

    def ping(self):
        pass  # TODO: see how to ping ORKG host to know if it is alive

    # FIXME: remove after system stabling
    def pagination_activated(self) -> bool:
        self.backend._append_slash = True
        return 'pageable' in self.backend.resources.GET().json()

    def wrap_response(self, response=None, status_code: str = None, content: Union[list, dict] = None,
                      url: str = None) -> OrkgResponse:
        is_paged = self.pagination_activated()
        return OrkgResponse(response=response, status_code=status_code, content=content, url=url, paged=is_paged)

