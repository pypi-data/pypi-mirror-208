from __future__ import annotations

import logging
from types import TracebackType
from typing import Any, Final, Iterator, Optional, Type, cast

import backoff
from requests import Response, Session

from .constants import GRAPH_API_URL, GRAPH_API_VERSIONS
from .dataclasses import AppUsageDetails, GraphAPIResponse, TokenDebugPayload
from .error_code import GraphAPICommonErrorCode
from .exceptions import (
    GraphAPIApplicationError,
    GraphAPIError,
    GraphAPIServiceError,
    GraphAPITokenError,
    GraphAPIUsageError,
    InvalidAccessToken,
    InvalidGraphAPIVersion,
)
from .typings import ErrorCodeExceptionMap, GraphAPIQueryResult, JSONTypeSimple

logger = logging.getLogger(__name__)


class GraphAPIClient:
    """
    A small client built to interact with the Facebook social graph:
    https://developers.facebook.com/docs/graph-api/overview

    This is currently built minimally for distribution in Dash Hudson
    services where JSON-based requests need to be handled.

    The following functionality is currently unsupported when
    comparing to the official facebook-sdk:
        - HMAC authentication
        - batch request handling
        - file uploading
        - generating oauth redirect urls

    For now API access is provisioned through access tokens,
    if you are unfamiliar with how this works see the following:
    https://developers.facebook.com/docs/facebook-login
    """

    DEFAULT_CODE_EXCEPTION_MAP: Final[ErrorCodeExceptionMap] = {
        (GraphAPICommonErrorCode.API_UNKNOWN.value, None): GraphAPIServiceError,
        (GraphAPICommonErrorCode.API_METHOD.value, None): GraphAPIServiceError,
        (GraphAPICommonErrorCode.API_PERMISSION_DENIED.value, None): GraphAPIApplicationError,
        (GraphAPICommonErrorCode.APPLICATION_BLOCKED_TEMP.value, None): GraphAPIApplicationError,
        (GraphAPICommonErrorCode.API_SESSION.value, None): GraphAPITokenError,
        (GraphAPICommonErrorCode.ACCESS_TOKEN_EXPIRED.value, None): GraphAPITokenError,
        (GraphAPICommonErrorCode.APPLICATION_LIMIT_REACHED.value, None): GraphAPIUsageError,
        (GraphAPICommonErrorCode.API_TOO_MANY_CALLS.value, None): GraphAPIUsageError,
        (GraphAPICommonErrorCode.PAGE_RATE_LIMIT_REACHED.value, None): GraphAPIUsageError,
        (GraphAPICommonErrorCode.CUSTOM_RATE_LIMIT_REACHED.value, None): GraphAPIUsageError,
    }

    def __init__(
        self,
        access_token: str,
        version: str,
        global_timeout: Optional[int] = None,
        params_to_mask: Optional[list[str]] = None,
        retry_params: Optional[dict] = None,
        disable_logger: Optional[bool] = False,
        code_exception_map: Optional[ErrorCodeExceptionMap] = None,
    ) -> None:
        """
        Initialize the API client
        :param access_token: An access token provisioned through Facebook login
        :param version: The Graph API version to use (ex: 12.0)
        :param global_timeout: A global request timeout to set
        :param params_to_mask: A list of query parameter names to mask when formatting
            exception messages
        :param disable_logger Disables exception logging if truthy
        :param retry_config Params for https://github.com/litl/backoff#backoffon_exception
        :param code_exception_map: A an error code -> exception map / configuration
        """
        if not access_token or not isinstance(access_token, str):
            raise InvalidAccessToken
        if version not in GRAPH_API_VERSIONS:
            raise InvalidGraphAPIVersion(version)

        self.version = f'v{version}'
        self.global_timeout = global_timeout
        self.params_to_mask = params_to_mask
        self.disable_logger = disable_logger
        # Defaulting to max_tries=0 disables retrying by default
        self.retry_params = retry_params or {'exception': tuple(), 'max_tries': 0}

        self.code_exception_map = self.DEFAULT_CODE_EXCEPTION_MAP
        if code_exception_map:
            self.code_exception_map = {
                **self.DEFAULT_CODE_EXCEPTION_MAP,
                **code_exception_map,
            }

        self._access_token = access_token
        self._session = Session()
        self._session.params = {'access_token': self._access_token}

    def get(
        self,
        path: str,
        params: Optional[Any] = None,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
    ) -> GraphAPIResponse:
        """
        :param path: A path pointing to an edge or node
            (ex: /<page_id>/conversations)
        Performs a GET request to the Graph API
        :param params: Query parameters to be included with the request
        :param timeout: A custom timeout for the request (seconds)
        :param retry_params: Retry params override
        :return: An instance of GraphAPIResponse
        """
        return self._do_request(
            method='GET',
            path=path,
            params=params,
            timeout=timeout,
            retry_params=retry_params,
        )

    def post(
        self,
        path: str,
        data: Any,
        params: Optional[Any] = None,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
    ) -> GraphAPIResponse:
        """
        Performs a POST request to the Graph API
        :param path: A path pointing to an edge or node
            (ex: /<page_id>/conversations | /<page_id>)
        :param data: The request body to be included
        :param params: Query parameters to be included with the request
        :param timeout: A custom timeout for the request (seconds)
        :param retry_params: Retry params override
        :return: An instance of GraphAPIResponse
        """
        return self._do_request(
            method='POST',
            path=path,
            params=params,
            data=data,
            timeout=timeout,
            retry_params=retry_params,
        )

    def delete(
        self,
        path: str,
        params: Optional[Any] = None,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
    ) -> GraphAPIResponse:
        """
        Performs a DELETE request to the Graph API
        :param path: A path pointing to a node
            (ex: /<video_id>)
        :param params: Query parameters to be included with the request
        :param timeout: A custom timeout for the request (seconds)
        :param retry_params: Retry params override
        :return: An instance of GraphAPIResponse
        """
        return self._do_request(
            method='DELETE',
            path=path,
            params=params,
            timeout=timeout,
            retry_params=retry_params,
        )

    def debug_token(self, client_id: str, client_secret: str) -> TokenDebugPayload:
        """
        Method for debugging the contained access token
        :param client_id: Meta developer app client ID
        :param client_secret: Meta developer app client secret
        :return: A parsed token debug payload
        """
        result = self.get(
            'debug_token',
            params={
                'access_token': f'{client_id}|{client_secret}',
                'input_token': self._access_token,
            },
        )
        return TokenDebugPayload.from_source_data(cast(dict, result.data))

    def _do_request(
        self,
        method: str,
        path: str,
        params: Optional[Any] = None,
        data: Optional[Any] = None,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
    ) -> GraphAPIResponse:
        """
        Handle Graph API requests. Raise if error body detected and lets ambiguous network
        errors propagate.
        :param method: The HTTP request method
        :param path: A path pointing to an edge or node (ex: /<page_id>/conversations)
        :param params: Query parameters to be included with the request
        :param data: The request body to be included
        :param timeout: A custom timeout for the request (seconds)
        :param retry_params: Retry params override
        :return: An instance of GraphAPIResponse
        """

        @backoff.on_exception(backoff.expo, **(retry_params or self.retry_params))
        def _retry_parameterizer() -> GraphAPIResponse:
            response = self._session.request(
                method=method,
                url=f'{GRAPH_API_URL}/{self.version}/{path}',
                params=params,
                data=data,
                timeout=timeout or self.global_timeout,
            )
            result, paging = self._parse_response_body_or_raise(response)

            return GraphAPIResponse(
                app_usage_details=AppUsageDetails.from_header(response),
                data=result,
                paging=paging,
            )

        return _retry_parameterizer()

    def _parse_response_body_or_raise(
        self, response: Response
    ) -> tuple[GraphAPIQueryResult, Optional[JSONTypeSimple]]:
        """
        Parse Graph API response body and raise if error details present
        :param response: A response from the Graph API
        :return: Parsed request body and optional paging params
        """
        response_body = response.json()
        error_details = response_body.get('error')
        if error_details:
            code_key = (error_details.get('code'), error_details.get('error_subcode'))
            # Raise a specific exception if a code mapping is set, custom exceptions take priority
            exc_type = self.code_exception_map.get(code_key, GraphAPIError)
            # Log & raise default GraphAPIError if no mapping was found
            exc = exc_type(
                response=response,
                error_details=error_details,
                params_to_mask=self.params_to_mask,
            )
            if not self.disable_logger:
                logger.error(str(exc))
            raise exc
        # If 'data' is present, it means the result is a list of graph nodes and may have
        # paging params as well
        if 'data' in response_body:
            return response_body['data'], response_body.get('paging')
        # If not, the response body is a single graph node without paging params
        return response_body, None

    def _get_paginated_results(self, path: str, params: JSONTypeSimple) -> Iterator[JSONTypeSimple]:
        """
        Simple helper used for iterating over paged-results
        TODO: Could be exposed for general use but should implement complete feature-set
        TODO: If exposed for public use, consider return type a bit
        :param path: Path to pass to self.get
        :param params: Params to pass to self.get
        :return: Iterator that yields paged results
        """
        while True:
            result = self.get(path=path, params=params)
            items = cast(list[JSONTypeSimple], result.data)
            for i in items:
                yield i

            if not result.after_cursor:
                break
            params['after'] = result.after_cursor

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self._session.close()
