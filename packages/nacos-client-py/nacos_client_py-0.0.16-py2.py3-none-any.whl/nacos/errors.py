# ruff: noqa: N818
import functools
import http
import typing

import httpx


class BaseError(Exception):
    """ 基异常 """

    pass


class RequestError(BaseError):
    """请求异常"""

    def __init__(self, message: str, *, request: httpx.Request):
        """__init__

        Parameters
        ----------
        message :
            异常信息
        request :
            请求对象
        """
        super().__init__(message)
        self.request = request


class Timeout(RequestError):
    """请求超时异常"""

    pass


class ResponseError(BaseError):
    """响应异常"""

    def __init__(
        self, message: str, *, request: httpx.Request, response: httpx.Response
    ):
        """__init__

        Parameters
        ----------
        message :
            异常信息
        request :
            请求对象
        response :
            响应对象
        """
        super().__init__(message)
        self.request = request
        self.response = response


### client error ###
class ClientError(ResponseError):
    """客户端异常"""

    code = "invalid_argument"


class Canceled(ClientError):
    """请求取消"""

    code = "canceled"


class InvalidArgument(ClientError):
    """参数错误"""

    code = "invalid_argument"


class Malformed(ClientError):
    """请求格式错误"""

    code = "malformed"


class DeadlineExceeded(ClientError):
    """请求过期"""

    code = "deadline_exceeded"


class NotFound(ClientError):
    """资源不存在"""

    code = "not_found"


class BadRoute(ClientError):
    """请求路由错误"""

    code = "bad_route"


class AlreadyExists(ClientError):
    """资源已存在"""

    code = "already_exists"


class PermissionDenied(ClientError):
    """权限不足"""

    code = "permission_denied"


class Unauthenticated(ClientError):
    """未认证"""

    code = "unauthenticated"


class ResourceExhausted(ClientError):
    """资源耗尽"""

    code = "resource_exhausted"


class FailedPrecondition(ClientError):
    """请求前置条件失败"""

    code = "failed_precondition"


class Aborted(ClientError):
    """请求中止"""

    code = "aborted"


class OutOfRange(ClientError):
    """请求参数超出范围"""

    code = "out_of_range"


### server error ###
class ServerError(ResponseError):
    """服务端异常"""

    code = "internal"


class Unknown(ServerError):
    """未知异常"""

    code = "unknown"


class Unimplemented(ServerError):
    """未实现"""

    code = "unimplemented"


class Internal(ServerError):
    """内部错误"""

    code = "internal"


class Unavailable(ServerError):
    """服务不可用"""

    code = "unavailable"


class DataLoss(ServerError):
    """数据丢失"""

    code = "dataloss"


def _unify_error(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except httpx.TimeoutException as e:
            raise Timeout(str(e), request=e.request) from e
        except httpx.RequestError as e:
            raise RequestError(str(e), request=e.request) from e

    return wrapper


_STATUS_CODE_CLIENT_ERROR_MAPPING = {
    http.HTTPStatus.REQUEST_TIMEOUT: DeadlineExceeded,
    http.HTTPStatus.UNPROCESSABLE_ENTITY: InvalidArgument,
    http.HTTPStatus.NOT_FOUND: NotFound,
    http.HTTPStatus.CONFLICT: AlreadyExists,
    http.HTTPStatus.FORBIDDEN: PermissionDenied,
    http.HTTPStatus.UNAUTHORIZED: Unauthenticated,
    http.HTTPStatus.TOO_MANY_REQUESTS: ResourceExhausted,
    http.HTTPStatus.PRECONDITION_FAILED: FailedPrecondition,
}

_STATUS_CODE_SERVER_ERROR_MAPPING = {
    http.HTTPStatus.INTERNAL_SERVER_ERROR: Internal,
    http.HTTPStatus.NOT_IMPLEMENTED: Unimplemented,
    http.HTTPStatus.SERVICE_UNAVAILABLE: Unavailable,
}


def _default_response_to_exception(response: httpx.Response):
    if response.is_success:
        return
    exception: typing.Union[typing.Type[ClientError], typing.Type[ServerError]]
    if response.is_client_error:
        exception = _STATUS_CODE_CLIENT_ERROR_MAPPING.get(
            http.HTTPStatus(response.status_code), ClientError
        )
        type_ = "Client Error"
    elif response.is_server_error:
        exception = _STATUS_CODE_SERVER_ERROR_MAPPING.get(
            http.HTTPStatus(response.status_code), ServerError
        )
        type_ = "Server Error"
    else:
        raise RuntimeError(f"Unexpected response: {response}")
    message = (
        f"{type_}: '{exception.code}' for url '{response.url}'. Response: {response.read()}"
    )
    raise exception(message, request=response.request, response=response)
