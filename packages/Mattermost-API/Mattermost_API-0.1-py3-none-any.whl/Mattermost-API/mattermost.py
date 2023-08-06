from mm_uploads_api import Uploads
from mm_bleve_api import Bleve
from mm_compliance_api import Compliance
from mm_elasticsearch_api import Elasticsearch
from mm_exports_api import  Exports
from mm_imports_api import Imports
from mm_int_actions_api import IntegrationActions
from mm_opengraph_api import Opengraph
from mm_permissions_api import Permissions
from mm_terms_of_service_api import TermsOfService
from mm_usage_api import Usage


class MattermostAPI:
    def __init__(self, token: str, server_url: str):
        self.token = token
        self.server_url = server_url

    @property
    def uploads(self):
        return Uploads(token=self.token, server_url=self.server_url)

    @property
    def blevels(self):
        return Bleve(token=self.token, server_url=self.server_url)

    @property
    def compliance(self):
        return Compliance(token=self.token, server_url=self.server_url)

    @property
    def elasticsearch(self):
        return Elasticsearch(token=self.token, server_url=self.server_url)

    @property
    def exports(self):
        return Exports(token=self.token, server_url=self.server_url)

    @property
    def imports(self):
        return Imports(token=self.token, server_url=self.server_url)

    @property
    def integrationactions(self):
        return IntegrationActions(token=self.token, server_url=self.server_url)

    @property
    def opengraph(self):
        return Opengraph(token=self.token, server_url=self.server_url)

    @property
    def permissions(self):
        return Permissions(token=self.token, server_url=self.server_url)

    @property
    def terms(self):
        return TermsOfService(token=self.token, server_url=self.server_url)

    @property
    def usage(self):
        return Usage(token=self.token, server_url=self.server_url)



