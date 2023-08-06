from typing import Union, List, Dict
from Mattermost_Base import Base


class Opengraph(Base):
    def __init__(self, token: str, server_url: str):
        super().__init__(token, server_url)
        self.api_url = f"{self.base_url}/opengraph"

    def get_og_mdata_for_url(self, url: str) -> dict:
        """
        Get Open Graph Metadata for a specif URL.
        Use the Open Graph protocol to get some generic metadata about a URL.
        Used for creating link previews.

        Minimum server version: 3.10
        No permission required but must be logged in.

        :param url: The URL to get Open Graph Metadata.
        :return: Open Graph retrieval.
        """

        url = f"{self.api_url}/"

        self.reset()
        self.add_application_json_header()
        self.add_to_json('url', url)

        return self.request(url, request_type='POST', body=True)