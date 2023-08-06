from typing import Union

import requests
from requests.exceptions import HTTPError


class EngineClientError(Exception):
    pass


class EngineClient:
    def __init__(self, base_url, token, timeout=30):
        self._base_url = base_url
        self._headers = {"X-Auth-Token": token}
        self._timeout = timeout

    def push_action(self, subject_id: str, action: str, payload: dict) -> None:
        endpoint = f"{self._base_url}/api/v1/subjects/{subject_id}/props/?a={action}"
        data = {"payload": payload}
        response = requests.post(endpoint, json=data, headers=self._headers, timeout=self._timeout)
        self._raise_for_status(response)

    def get_pluggable_props(self, subject_id: str, props: str, **kwargs) -> Union[dict, list]:
        params = {"p": props, **kwargs}
        endpoint = f"{self._base_url}/api/v1/subjects/{subject_id}/props/"
        response = requests.get(endpoint, headers=self._headers, params=params, timeout=self._timeout)
        self._raise_for_status(response)
        return response.json()

    def direct_get(self, subject_id: str, path: str, params: dict) -> Union[dict, list]:
        endpoint = self._format_direct_endpoint(subject_id, path)
        response = requests.get(endpoint, headers=self._headers, params=params, timeout=self._timeout)
        self._raise_for_status(response)
        return response.json()

    def direct_post(
        self, subject_id: str, path: str, params: dict, data: Union[dict, list]
    ) -> Union[dict, list]:
        endpoint = self._format_direct_endpoint(subject_id, path)
        response = requests.post(
            endpoint, headers=self._headers, params=params, json=data, timeout=self._timeout
        )
        self._raise_for_status(response)
        return response.json()

    def direct_put(
        self, subject_id: str, path: str, params: dict, data: Union[dict, list]
    ) -> Union[dict, list]:
        endpoint = self._format_direct_endpoint(subject_id, path)
        response = requests.put(
            endpoint, headers=self._headers, params=params, json=data, timeout=self._timeout
        )
        self._raise_for_status(response)
        return response.json()

    def direct_patch(
        self, subject_id: str, path: str, params: dict, data: Union[dict, list]
    ) -> Union[dict, list]:
        endpoint = self._format_direct_endpoint(subject_id, path)
        response = requests.patch(
            endpoint, headers=self._headers, params=params, json=data, timeout=self._timeout
        )
        self._raise_for_status(response)
        return response.json()

    def direct_delete(self, subject_id: str, path: str, params: dict) -> None:
        endpoint = self._format_direct_endpoint(subject_id, path)
        response = requests.delete(endpoint, headers=self._headers, params=params, timeout=self._timeout)
        self._raise_for_status(response)

    def _format_direct_endpoint(self, subject_id, path):
        return f"{self._base_url}/s/{subject_id}{path}"

    @staticmethod
    def _raise_for_status(response):
        try:
            response.raise_for_status()
        except HTTPError as e:
            raise EngineClientError from e
