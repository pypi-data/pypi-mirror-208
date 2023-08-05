from __future__ import annotations

from typing import Optional
from threading import Lock

import os
import logging

from .request_type import RequestType
from .network_response import NetworkResponse
from .network_manager_base import NetworkManagerBase
from .user_data import UserData


class NetworkManager(NetworkManagerBase):

    __instanceLock = Lock()
    __instance: Optional[NetworkManager] = None

    @classmethod
    def instance(cls) -> NetworkManager:
        if cls.__instance is None:
            with cls.__instanceLock:
                if cls.__instance is None:
                    cls.__instance = cls()

        return cls.__instance

    def __init__(self) -> None:
        super().__init__()

        self.__userData = UserData()

    @classmethod
    def serverUrl(cls) -> str:
        serverUrl = os.environ["CTX_API_URL"]
        return f"{serverUrl}api/v1/"

    @property
    def _apiToken(self) -> Optional[str]:
        return self.__userData.apiToken

    @property
    def hasStoredCredentials(self) -> bool:
        return self.__userData.hasStoredCredentials

    def __authenticate(self) -> NetworkResponse:
        # authenticate using credentials stored in requests.Session.auth

        response = self._requestManager.post(
            endpoint = self.loginEndpoint,
            headers = self._requestHeader()
        )

        if self.apiTokenKey in response.json:
            self.__userData.apiToken = response.json[self.apiTokenKey]

        if self.refreshTokenKey in response.json:
            self.__userData.refreshToken = response.json[self.refreshTokenKey]

        return response

    def authenticate(self, username: str, password: str, storeCredentials: bool = True) -> NetworkResponse:
        """
            Authenticates user with provided credentials

            Parameters
            ----------
            username : str
                Coretex.ai username
            password : str
                Coretex.ai password
            storeCredentials : bool
                If true credentials will be stored in User object for reuse

            Returns
            -------
            NetworkResponse -> NetworkResponse object containing the full response info

            Example
            -------
            >>> from coretex.networking import NetworkManager
            \b
            >>> response = NetworkManager.instane().authenticate(username = "dummy@coretex.ai", password = "123456")
            >>> if response.hasFailed():
                    print("Failed to authenticate")
        """

        self._requestManager.setAuth(username, password)

        if storeCredentials:
            self.__userData.username = username
            self.__userData.password = password

        # authenticate using credentials stored in requests.Session.auth
        return self.__authenticate()

    def authenticateWithRefreshToken(self, token: str) -> NetworkResponse:
        """
            Authenticates user with provided refresh token

            Parameters
            ----------
            token : str
                refresh token

            Returns
            -------
            NetworkResponse -> NetworkResponse object containing the full response info
        """

        self.__userData.refreshToken = token
        return self.refreshToken()

    def authenticateWithStoredCredentials(self) -> NetworkResponse:
        """
            Authenticates user with credentials stored inside User object

            Returns
            -------
            NetworkResponse -> NetworkResponse object containing the full response info

            Raises
            ------
            ValueError -> if credentials are not found
        """

        if self.__userData.username is None or self.__userData.password is None:
            raise ValueError(">> [Coretex] Credentials not stored")

        return self.authenticate(self.__userData.username, self.__userData.password)

    def refreshToken(self) -> NetworkResponse:
        """
            Uses refresh token functionality to fetch new API access token

            Returns
            -------
            NetworkResponse -> NetworkResponse object containing the full response info
        """

        headers = self._requestHeader()

        if self.__userData.refreshToken is not None:
            headers[self.apiTokenHeaderField] = self.__userData.refreshToken

        networkResponse = self._requestManager.genericRequest(
            requestType = RequestType.post,
            endpoint = self.refreshEndpoint,
            headers = headers
        )

        if networkResponse.hasFailed():
            # the following logic should be removed as part of CTX-1659
            # it is needed for node authentication when refresh token issued on startup expires

            # if refresh failed try to login again
            if not self._requestManager.isAuthSet:
                raise RuntimeError(">> [Coretex] Cannot login on user/refresh failure. Credentials not available")

            authResponse = self.__authenticate()
            if authResponse.hasFailed():
                # if both login and refresh failed, something is seriously wrong
                raise RuntimeError(">> [Coretex] Failed to login during on user/refresh failure")

            # the following line should be commented out as part of CTX-1659
            # as both node and workspace will use the same refresh token which duration will be enough to cover long running experiments
            raise RuntimeError(">> [Coretex] Failed to do API token refresh")
        elif self.apiTokenKey in networkResponse.json:
            self.__userData.apiToken = networkResponse.json[self.apiTokenKey]
            logging.getLogger("coretexpylib").debug(">> [Coretex] API token refresh was successful. API token updated")

        return networkResponse

    def shouldRetry(self, retryCount: int, response: NetworkResponse) -> bool:
        # Limit retry count to 3 times
        if retryCount == NetworkManager.MAX_RETRY_COUNT:
            return False

        # If we get unauthorized maybe API token is expired
        if response.isUnauthorized():
            self.refreshToken()
            return True

        return super().shouldRetry(retryCount, response)

    def reset(self) -> None:
        """
            Removes api and refresh token
        """

        self.__userData.apiToken = None
        self.__userData.refreshToken = None
