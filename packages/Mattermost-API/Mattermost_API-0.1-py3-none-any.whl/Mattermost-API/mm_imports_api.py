from typing import Union, List, Dict
from Mattermost_Base import Base


class Imports(Base):
    def __init__(self, token: str, server_url: str):
        super().__init__(token, server_url)
        self.api_url = f"{self.base_url}/imports"

    def list_import_files(self) -> dict:
        """
        Lists all available import files.

        Minimum server version: 5.31
        Must have manage_system permissions.

        :return: Import files list
        """

        url = f"{self.api_url}/"
        self.reset()

        return self.request(url, request_type='GET')
