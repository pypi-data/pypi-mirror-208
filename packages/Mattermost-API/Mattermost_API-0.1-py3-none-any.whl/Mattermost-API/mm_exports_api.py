from typing import Union, List, Dict
from Mattermost_Base import Base


class Exports(Base):
    def __init__(self, token: str, server_url: str):
        super().__init__(token, server_url)
        self.api_url = f"{self.base_url}/exports"

    def list_export_files(self) -> dict:
        """
        Lists all available export files.

        Minimum server version: 5.33
        Must have manage_system permissions.

        :return: List of all available export files
        """

        url = f"{self.api_url}/"

        self.reset()

        return self.request(url, request_type='GET')

    def download_export_file(self, export_name: str) -> dict:
        """
        Downloads an export file.

        Minimum server version: 5.33
        Must have manage_system permissions.

        :param export_name: The name of the export file to download
        :return: Download info
        """

        url = f"{self.api_url}/{export_name}"

        self.reset()
        self.add_to_json('export_name', export_name)

        return self.request(url, request_type='GET')

    def delete_export_file(self, export_name: str) -> dict:
        """
        Deletes an export file.

        Minimum server version: 5.33
        Must have manage_system permissions.

        :param export_name: The name of the export file to delete
        :return: Delete info
        """

        url = f"{self.api_url}/{export_name}"

        self.reset()
        self.add_to_json('export_name', export_name)

        return self.request(url, request_type='DEL')
