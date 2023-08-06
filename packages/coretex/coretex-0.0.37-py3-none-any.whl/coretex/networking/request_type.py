from enum import Enum


class RequestType(Enum):

    """
        Represents request types supported by NetworkManager
    """

    get = "GET"
    post = "POST"
    put = "PUT"
    delete = 'DELETE'
