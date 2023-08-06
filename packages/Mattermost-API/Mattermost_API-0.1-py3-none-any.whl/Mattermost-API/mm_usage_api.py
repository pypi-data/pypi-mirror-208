from typing import Union, List, Dict
from Mattermost_Base import Base


class Usage(Base):
    def __init__(self, token: str, server_url: str):
        super().__init__(token, server_url)
        self.api_url = f"{self.base_url}/usage"

    def get_current_post_usage(self) -> dict:
        """
        Retrieve rounded off total no. of posts for this instance.
        Example: returns 4000 instead of 4321

        Must be authenticated.
        Minimum server version: 7.0

        :return: Total no. of posts returned successfully
        """

        url = f"{self.api_url}/posts"

        self.reset()

        return self.request(url, request_type='GET')

    def get_total_file_storage_usage(self) -> dict:
        """
        Get the total file storage usage for the instance in bytes
        rounded down to the most significant digit.
        Example: returns 4000 instead of 4321

        Must be authenticated.
        Minimum server version: 7.1

        :return: Total file storage usage for the instance in bytes rounded down to the most significant digit
        """

        url = f"{self.api_url}/storage"

        self.reset()

        return self.request(url, request_type='GET')
