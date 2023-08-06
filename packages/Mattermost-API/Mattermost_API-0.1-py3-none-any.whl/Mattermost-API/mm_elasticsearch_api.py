from typing import Union, List, Dict
from Mattermost_Base import Base


class Elasticsearch(Base):
    def __init__(self, token: str, server_url: str):
        super().__init__(token, server_url)
        self.api_url = f"{self.base_url}/elasticsearch"

    def test_elast_config(self) -> dict:
        """
        Test the current Elasticsearch configuration to see
        if the Elasticsearch server can be contacted successfully.
        Optionally provide a configuration in the request body to test.
        If no valid configuration is present in the request body
        the current server configuration will be tested.

        Minimum server version: 4.1
        Must have manage_system permission.

        :return: Elasticsearch retreival
        """

        url = f"{self.api_url}/test"
        self.reset()

        return self.request(url, request_type='POST')

    def purge_elast_indexes(self) -> dict:

        """
        Deletes all Elasticsearch indexes and their contents.
        After calling this endpoint, it is necessary to schedule
        a new Elasticsearch indexing job to repopulate the indexes.

        Minimum server version: 4.1
        Must have manage_system permission.

        :return: Elasticsearch retreival
        """

        url = f"{self.api_url}/purge_indexes"
        self.reset()

        return self.request(url, request_type='POST')