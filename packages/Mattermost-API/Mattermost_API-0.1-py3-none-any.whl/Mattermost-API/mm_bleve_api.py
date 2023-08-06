from typing import Union, List, Dict
from Mattermost_Base import Base


class Bleve(Base):
    def __init__(self, token: str, server_url: str):
        super().__init__(token, server_url)
        self.api_url = f"{self.base_url}/bleve"

    def purge_bleve(self) -> dict:
        """
        Deletes all Bleve indexes and their contents.
        After calling this endpoint, it is necessary to schedule
        a new Bleve indexing job to repopulate the indexes.

        Minimum server version: 5.24
        Must have sysconsole_write_experimental permission.

        :param status: The size of the file to upload in bytes.
        :return: Bleve retreival
        """

        url = f"{self.api_url}/purge_indexes"
        self.reset()

        return self.request(url, request_type='POST')