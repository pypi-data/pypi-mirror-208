from rest_framework.response import Response
from typing import Optional


class ApiResponse(Response):
    def __init__(self, msg: str, data: Optional = None, status: int = 200):
        resp = {
            "succeeded": status in range(200, 300),
            "msg": msg,
            "data": data
        }
        super().__init__(data=resp, status=status)


class SuccessApiResponse(ApiResponse):
    def __init__(self, msg, data):
        super(SuccessApiResponse, self).__init__(msg, data)


class FailureApiResponse(ApiResponse):
    def __init__(self, msg, data=None):
        super(FailureApiResponse, self).__init__(msg, data, status=400)


class ServerErrorApiResponse(ApiResponse):
    def __init__(self):
        super(ServerErrorApiResponse, self).__init__("Server error",
                                                     status=500)
