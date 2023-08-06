from typing import Union
import os

import requests


class Base:
    def __init__(self, token: str, server_url: str, version: str = "v4"):
        self.token = f"Bearer {token}"
        self.headers = {'Authorization': f'{self.token}'}
        self.base_url = server_url.rstrip('/') + '/api/' + version.rstrip('/')
        self.body = None
        self.data = None
        self.cookies = None
        self.error_desc = None
        self.files = None

    def reset(self) -> None:
        """
            Сбрасывает все данные запроса в дефолтные значения.
        """
        self.body = None
        self.data = None
        self.cookies = None
        self.headers = {'Authorization': f'{self.token}'}

    def add_cookie(self, key: str, value: str) -> None:
        """
            Добавляет запись {key:value} в cookies.

            :param key: Ключ для добавления в cookies.
            :type key: :obj:`base.String`
            :param value: Значение ключа для добавления в cookies.
            :type value: :obj:`base.String`

        """
        if self.cookies is None:
            self.cookies = {}
        self.cookies.update({key: value})

    def add_query_param(self, key: str, value: Union[str, dict, list, tuple, int, bool]) -> None:
        """
            Добавляет запись {key:value} в json Body.

            :param key: Ключ для добавления в query Parameters.
            :type key: :obj:`base.String`
            :param value: Значение ключа для добавления в query Parameters.
            :type value: :obj:`base.String`

        """
        if self.data is None:
            self.data = {}
        self.data.update({key: value})

    def add_application_json_header(self) -> None:
        """
            Добавляет заголовок в запрос для отправки JSON данных.
        """
        self.headers.update({'Content-Type': 'application/json'})

    def add_application_www_form_header(self) -> None:
        """
            Добавляет заголовок в запрос для отправки JSON данных.
        """
        self.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})

    def add_to_json(self, key: str, value: Union[str, dict, list, tuple, int, bool]) -> None:
        """
          Добавляет запись {key:value} в json Body.

          :param key: Ключ для добавления в json Body.
          :type key: :obj:`base.String`
          :param value: Значение ключа для добавления в json Body.
          :type value: :obj:`base.String`

        """
        if self.body is None:
            self.body = {}
        self.body.update({key: value})

    def add_file(self, file_path: str) -> None:
        """
        Добавляет файл к телу запроса.

        :param file_path: Полный путь до файла.
        """

        data = None

        try:
            with open(file_path, 'r') as f:
                data = f.read()
        except Exception as err:
            return

        if self.files is None:
            self.files = {}

        filename = os.path.basename(file_path)

        self.files.update({filename: data})

    def request(self, url: str,
                params: bool = None,
                body: bool = None,
                cookies: bool = None,
                files: bool = None,
                request_type: str = 'GET') -> dict:
        """
          Делает запрос с указанными параметрами по URL

          :param url: URL запроса.
          :type url: :obj:`base.String`
          :param params: Передавать ли в запросе query Parameters.
          :type params: :obj:`base.Boolean`
          :param body: Передавать ли в запросе json Body.
          :type body: :obj:`base.Boolean`
          :param cookies: Передавать ли в запросе cookies.
          :type cookies: :obj:`base.Boolean`
          :param files: Прикрепленные файлы.
          :param request_type: Метод запроса.
          :type request_type: :obj:`base.String`
          :return: Словарь с результатами запроса.
          :rtype: :obj:'typing.Dict'
        """

        requests_types = {
            'GET': requests.get,
            'POST': requests.post,
            'PUT': requests.put,
            'DELETE': requests.delete,
            'PATCH': requests.patch,
        }

        try:
            data = self.data if params is not None else None
            json = self.body if body is not None else None
            cookies = self.cookies if cookies is not None else None
            files = self.files if files is not None else None

            response = requests_types[request_type](url=url,
                                                    headers=self.headers,
                                                    json=json,
                                                    data=data,
                                                    cookies=cookies,
                                                    files=files)
            if response.status_code in (200, 201, 204):
                return response.json()
            elif response.status_code == 401:
                print("UnauthorizedError", response.json()['message'])
        except Exception as err:
            self.error_desc = err

        print(f"Request ERROR: {self.error_desc}")
        return {}
