from typing import Union, List, Dict
from Mattermost_Base import Base


class Permissions(Base):
    def __init__(self, token: str, server_url: str):
        super().__init__(token, server_url)
        self.api_url = f"{self.base_url}/permissions"

    def return_sys_console_ancillary_permissions(self) -> dict:
        """
        Returns all the ancillary permissions for the corresponding system console subsection
        permissions appended to the requested permission subsections.

        Minimum server version: 5.35
        :return: Successfully returned all ancillary and requested permissions
        """

        url = f"{self.api_url}/ancillary"
        self.reset()

        return self.request(url, request_type='GET')
