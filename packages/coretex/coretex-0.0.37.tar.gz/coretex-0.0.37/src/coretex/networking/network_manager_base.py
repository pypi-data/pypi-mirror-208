from pathlib import Path
from typing import Optional, Any, Dict
from abc import ABC, abstractmethod

import json

from .requests_manager import RequestsManager
from .request_type import RequestType
from .network_response import HttpCode, NetworkResponse


class NetworkManagerBase(ABC):

    MAX_RETRY_COUNT = 3

    def __init__(self) -> None:
        self._requestManager = RequestsManager(self.serverUrl(), 20, 30)

        # Override NetworkManager to update values
        self.loginEndpoint: str = "user/login"
        self.refreshEndpoint: str = "user/refresh"

        self.apiTokenHeaderField: str = "api-token"

        self.apiTokenKey: str = "token"
        self.refreshTokenKey: str = "refresh_token"

    @classmethod
    @abstractmethod
    def serverUrl(cls) -> str:
        pass

    @property
    @abstractmethod
    def _apiToken(self) -> Optional[str]:
        pass

    def _requestHeader(self) -> Dict[str, str]:
        header = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Cache-Control": "no-cache",
            "Accept-Encoding": "gzip, deflate",
            "Content-Length": "0",
            "Connection": "keep-alive",
            "cache-control": "no-cache"
        }

        if self._apiToken is not None:
            header[self.apiTokenHeaderField] = self._apiToken

        return header

    def genericDownload(
        self,
        endpoint: str,
        destination: str,
        parameters: Optional[Dict[str, Any]] = None,
        retryCount: int = 0
    ) -> NetworkResponse:
        """
            Downloads file to the given destination

            Parameters
            ----------
            endpoint : str
                API endpoint
            destination : str
                path to save file
            parameters : Optional[dict[str, Any]]
                request parameters (not required)
            retryCount : int
                number of function calls if request has failed

            Returns
            -------
            NetworkResponse as response content to request

            Example
            -------
            >>> from coretex import NetworkManager
            \b
            >>> response = NetworkManager.instance().genericDownload(
                    endpoint = "dummyObject/download",
                    destination = "path/to/destination/folder"
                )
            >>> if response.hasFailed():
                    print("Failed to download the file")
        """

        headers = self._requestHeader()

        if parameters is None:
            parameters = {}

        response = self._requestManager.get(endpoint, headers, jsonObject = parameters)

        if self.shouldRetry(retryCount, response):
            print(">> [Coretex] Retry count: {0}".format(retryCount))
            return self.genericDownload(endpoint, destination, parameters, retryCount + 1)

        if response.raw.ok:
            destinationPath = Path(destination)
            if destinationPath.is_dir():
                raise RuntimeError(">> [Coretex] Destination is a directory not a file")

            if destinationPath.exists():
                destinationPath.unlink(missing_ok = True)

            destinationPath.parent.mkdir(parents = True, exist_ok = True)

            with open(destination, "wb") as downloadedFile:
                downloadedFile.write(response.raw.content)

        return response

    def genericUpload(
        self,
        endpoint: str,
        files: Any,
        parameters: Optional[Dict[str, Any]] = None,
        retryCount: int = 0
    ) -> NetworkResponse:
        """
            Uploads files to Cortex.ai

            Parameters
            ----------
            endpoint : str
                API endpoint
            files : Any
                files
            parameters : Optional[dict[str, Any]]
                request parameters (not required)
            retryCount : int
                number of function calls if request has failed

            Returns
            -------
            NetworkResponse -> NetworkResponse object containing the full response info

            Example
            -------
            >>> from coretex import NetworkManager
            \b
            >>> localFilePath = "path/to/file/filename.ext"
            >>> with open(localFilePath, "rb") as file:
                    files = [
                        ("file", ("filename.ext", file, "application/zip"))
                    ]
            \b
                    response = NetworkManager.instance().genericUpload(
                        endpoint = "dummy/upload",
                        files = files,
                    )
            >>> if response.hasFailed():
                    print("Failed to upload the file")
        """

        headers = self._requestHeader()
        del headers['Content-Type']

        if parameters is None:
            parameters = {}

        networkResponse = self._requestManager.genericRequest(RequestType.post, endpoint, headers, parameters, files)

        if self.shouldRetry(retryCount, networkResponse):
            print(">> [Coretex] Retry count: {0}".format(retryCount))
            return self.genericUpload(endpoint, files, parameters, retryCount + 1)

        return networkResponse

    def genericDelete(
        self,
        endpoint: str
    ) -> NetworkResponse:
        """
            Deletes Cortex.ai objects

            Parameters
            ----------
            endpoint : str
                API endpoint

            Returns
            -------
            NetworkResponse -> NetworkResponse object containing the full response info

            Example
            -------
            >>> from coretex import NetworkManager
            \b
            >>> response = NetworkManager.instance().genericDelete(
                    endpoint = "dummyObject/delete"
                )
            >>> if response.hasFailed():
                    print("Failed to delete the object")
        """

        return self._requestManager.genericRequest(RequestType.delete, endpoint, self._requestHeader())

    def genericJSONRequest(
        self,
        endpoint: str,
        requestType: RequestType,
        parameters: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        retryCount: int = 0
    ) -> NetworkResponse:
        """
            Sends generic http request with specified parameters

            Parameters
            ----------
            endpoint : str
                API endpoint
            requestType : RequestType
                request type
            parameters : Optional[dict[str, Any]]
                request parameters (not required)
            headers : Optional[dict[str, str]]
                headers (not required)
            retryCount : int
                number of function calls if request has failed

            Returns
            -------
            NetworkResponse -> NetworkResponse object containing the full response info

            Example
            -------
            >>> from coretex import NetworkManager
            \b
            >>> response = NetworkManager.instance().genericJSONRequest(
                    endpoint = "dummy/add",
                    requestType = RequestType.post,
                    parameters = {
                        "object_id": 1,
                    }
                )
            >>> if response.hasFailed():
                    print("Failed to add the object")
        """

        if headers is None:
            headers = self._requestHeader()

        if parameters is None:
            parameters = {}

        networkResponse = self._requestManager.genericRequest(requestType, endpoint, headers, json.dumps(parameters))

        if self.shouldRetry(retryCount, networkResponse):
            print(">> [Coretex] Retry count: {0}".format(retryCount))
            return self.genericJSONRequest(endpoint, requestType, parameters, headers, retryCount + 1)

        return networkResponse

    def shouldRetry(self, retryCount: int, response: NetworkResponse) -> bool:
        """
            Checks if network request should be repeated based on the number of repetitions
            as well as the response from previous repetition

            Parameters
            ----------
            retryCount : int
                number of repeated function calls
            response : NetworkResponse
                generated response after sending the request

            Returns
            -------
            bool -> True if the function call needs to be repeated,
            False if function was called 3 times or if request has not failed
        """

        # Limit retry count to 3 times
        if retryCount == NetworkManagerBase.MAX_RETRY_COUNT:
            return False

        return (
            response.statusCode == HttpCode.internalServerError or
            response.statusCode == HttpCode.serviceUnavailable
        )
