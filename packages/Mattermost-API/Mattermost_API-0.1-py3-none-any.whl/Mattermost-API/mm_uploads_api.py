from typing import Union, List, Dict
from Mattermost_Base import Base


class Uploads(Base):
    def __init__(self, token: str, server_url: str):
        super().__init__(token, server_url)
        self.api_url = f"{self.base_url}/uploads"

    def create_upload(self, channel_id: str,
                      filename: str,
                      file_size: int) -> dict:
        """
        Creates a new upload session.

        Minimum server version: 5.28
        Must have upload_file permission.

        :param channel_id: The ID of the channel to upload to.
        :param filename: The name of the file to upload.
        :param file_size: The size of the file to upload in bytes.
        :return: Upload creation successful.
        """

        url = f"{self.api_url}/"

        self.reset()
        self.add_application_json_header()
        self.add_to_json('channel_id', channel_id)
        self.add_to_json('filename', filename)
        self.add_to_json('file_size', file_size)

        return self.request(url, request_type='POST', body=True)

    def get_upload_session(self, upload_id: str) -> dict:
        """
        Gets an upload session that has been previously created.

        Must be logged in as the user who created the upload session.

        :param upload_id: The ID of the upload session to get.
        :return: Upload session
        """

        url = f"{self.api_url}/{upload_id}"
        self.reset()

        return self.request(url, request_type='GET')

    def perform_file_upload(self, upload_id: str, file_path: str = None) -> dict:
        """
        Starts or resumes a file upload.
        To resume an existing (incomplete) upload, data should be sent starting from the offset specified in the upload session object.

        The request body can be in one of two formats:
          - Binary file content streamed in request's body
          - multipart/form-data

        Must be logged in as the user who created the upload session.

        :param upload_id: The ID of the upload session the data belongs to.
        :param file_path: Full path to file.
        :return: Upload info.
        """

        url = f"{self.api_url}/{upload_id}"
        self.reset()
        self.add_application_www_form_header()

        if file_path is not None:
            self.add_file(file_path=file_path)

        return self.request(url, request_type='POST', files=True)



