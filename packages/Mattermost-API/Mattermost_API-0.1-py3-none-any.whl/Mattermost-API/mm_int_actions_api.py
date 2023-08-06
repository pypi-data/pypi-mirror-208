from typing import Union, List, Dict
from Mattermost_Base import Base


class IntegrationActions(Base):
    def __init__(self, token: str, server_url: str):
        super().__init__(token, server_url)
        self.api_url = f"{self.base_url}/actions/dialogs"

    def open_dialog(self, trigger_id: str,
                    url: str,
                    dialog: dict) -> dict:

        """
        Open an interactive dialog using a trigger ID provided by
        a slash command,or some other action payload.

        Minimum server version: 5.6
        No special permission.

        :param trigger_id: Trigger ID provided by other action
        :param url: The URL to send the submitted dialog payload to
        :param dialog: Post object to create
        :return: Dialog open successful
        """

        url = f"{self.api_url}/open"

        self.reset()
        self.add_application_json_header()
        self.add_to_json('trigger_id', trigger_id)
        self.add_to_json('url', url)
        self.add_to_json('dialog', dialog)

        return self.request(url, request_type='POST', body=True)

    def submit_dialog(self, url: str,
                      channel_id: str,
                      team_id: str,
                      submission: dict,
                      callback_id: str,
                      state: str,
                      cancelled: bool) -> dict:
        """
        Endpoint used by the Mattermost clients to submit a dialog.
        Minimum server version: 5.6
        No special permissions.

        :param url: The URL to send the submitted dialog payload to
        :param channel_id: Channel ID the user submitted the dialog from
        :param team_id: Team ID the user submitted the dialog from
        :param submission: String map where keys are element names and values are the element input values
        :param callback_id: Callback ID sent when the dialog was opened
        :param state: State sent when the dialog was opened
        :param cancelled: Set to true if the dialog was cancelled
        :return: Dialog submission successful
        """

        url = f"{self.api_url}/submit"

        self.reset()
        self.add_application_json_header()
        self.add_to_json('url', url)
        self.add_to_json('channel_id', channel_id)
        self.add_to_json('team_id', team_id)
        self.add_to_json('submission', submission)
        if callback_id is not None:
            self.add_to_json('callback_id', callback_id)
        if state is not None:
            self.add_to_json('state', state)
        if cancelled is not None:
            self.add_to_json('cancelled', cancelled)

        return self.request(url, request_type='POST', body=True)
