from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

from requests import Response

from .helpers import posix_2_datetime
from .typings import GraphAPIQueryResult, JSONTypeSimple


@dataclass(frozen=True)
class TokenDebugPayload:
    """
    Encapsulates a token debug payload from the Graph API
    See: https://developers.facebook.com/docs/facebook-login/guides/%20access-tokens/debugging
    """

    app_id: str
    type: str
    application: str
    data_access_expires_at: datetime
    expires_at: datetime
    is_valid: bool
    user_id: str
    scopes: list[str]
    granular_scopes: list[GranularScope]
    issued_at: Optional[datetime] = None  # Only present if token is long-lived

    @classmethod
    def from_source_data(cls, source_data: JSONTypeSimple) -> TokenDebugPayload:
        date_fields: JSONTypeSimple = {}
        for k in ['data_access_expires_at', 'expires_at', 'issued_at']:
            timestamp = source_data.pop(k, None)
            if timestamp:
                date_fields[k] = posix_2_datetime(timestamp)

        granular_scopes = source_data.pop('granular_scopes', [])
        if granular_scopes:
            granular_scopes = [GranularScope.from_source_data(s) for s in granular_scopes]

        return TokenDebugPayload(**source_data, **date_fields, granular_scopes=granular_scopes)


@dataclass(frozen=True)
class GranularScope:
    """
    Encapsulates a granular scope state returned via token debug payload
    See: https://developers.facebook.com/docs/facebook-login/guides/%20access-tokens/debugging
    """

    scope: str
    target_ids: Optional[list[str]] = None

    def contains_target_id(self, target_id: Union[int, str]) -> bool:
        if not self.target_ids:
            return True
        return str(target_id) in self.target_ids

    @classmethod
    def from_source_data(cls, source_data: JSONTypeSimple) -> GranularScope:
        return GranularScope(scope=source_data['scope'], target_ids=source_data.get('target_ids'))


@dataclass(frozen=True)
class UserScope:
    """
    Encapsulates a user state object returned by /me/permissions
    See: https://developers.facebook.com/docs/graph-api/reference/user/permissions/
    """

    permission: str
    status: str

    @property
    def is_granted(self) -> bool:
        return self.status == 'granted'


@dataclass(frozen=True)
class ConnectedPage:
    """
    Encapsulates a partial Page state
    See: https://developers.facebook.com/docs/graph-api/reference/page/
    """

    id: str
    access_token: str
    instagram_account_id: Optional[int] = None
    instagram_business_id: Optional[str] = None
    tasks: Optional[list[str]] = None

    def matches_id_set(self, page_id: int, instagram_account_id: Optional[int]) -> bool:
        page_id_matches = self.id == page_id
        if not instagram_account_id:
            return page_id_matches
        return page_id_matches and self.instagram_account_id == instagram_account_id

    @classmethod
    def from_source_data(cls, source_data: JSONTypeSimple) -> ConnectedPage:
        linked_instagram_account = source_data.get('instagram_business_account', {})
        return ConnectedPage(
            id=source_data['id'],
            access_token=source_data['access_token'],
            instagram_account_id=linked_instagram_account.get('ig_id'),
            instagram_business_id=linked_instagram_account.get('id'),
            tasks=source_data.get('tasks', []),
        )


@dataclass(frozen=True)
class PageWebhookSubscription:
    """
    Encapsulates a Webhook subscription state for a page
    See: https://developers.facebook.com/docs/graph-api/reference/page/subscribed_apps
    """

    category: str
    link: str
    name: str
    id: str
    subscribed_fields: list[str]


@dataclass(frozen=True)
class AppUsageDetails:
    """
    Encapsulates stats from X-App-Usage header:
    https://developers.facebook.com/docs/graph-api/overview/rate-limiting#headers
    """

    call_count: int
    total_time: int
    total_cputime: int

    @classmethod
    def from_header(cls, res: Response) -> AppUsageDetails:
        header_val = res.headers.get('X-App-Usage')
        app_usage_dict = json.loads(header_val) if header_val else {}

        return cls(
            call_count=app_usage_dict.get('call_count', 0),
            total_time=app_usage_dict.get('total_time', 0),
            total_cputime=app_usage_dict.get('total_cputime', 0),
        )


@dataclass
class GraphAPIResponse:
    """
    Encapsulates a Graph API response payload with parsed app usage headers
    """

    app_usage_details: AppUsageDetails
    data: GraphAPIQueryResult
    paging: Optional[JSONTypeSimple] = None

    @property
    def is_empty(self) -> bool:
        return not self.data

    @property
    def is_list(self) -> bool:
        return isinstance(self.data, list)

    @property
    def is_dict(self) -> bool:
        return isinstance(self.data, dict)

    @property
    def before_cursor(self) -> Optional[str]:
        return self.cursors.get('before')

    @property
    def after_cursor(self) -> Optional[str]:
        return self.cursors.get('after')

    @property
    def cursors(self) -> JSONTypeSimple:
        return self.paging.get('cursors', {}) if self.paging else {}
