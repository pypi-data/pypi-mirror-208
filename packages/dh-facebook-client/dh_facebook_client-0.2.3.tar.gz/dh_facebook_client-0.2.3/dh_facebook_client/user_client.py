from typing import Final, Optional, cast

from .client import GraphAPIClient
from .dataclasses import ConnectedPage, UserScope
from .helpers import first_true, format_fields_str

CONNECTED_PAGES_DEFAULT_LIMIT: Final = 100
CONNECTED_PAGES_FIELDS: Final = format_fields_str(
    [
        {'field_name': 'access_token'},
        {'field_name': 'tasks'},
        {
            'field_name': 'instagram_business_account',
            'sub_fields': [
                {
                    'field_name': 'ig_id',
                },
            ],
        },
    ],
)


class UserClient(GraphAPIClient):
    """
    Extends GraphAPIClient to include helpers for common User-based functionality
    """

    def get_user_scopes(self) -> list[UserScope]:
        """
        Return a list of scopes requested by the developer app at the User-level
        :return: List of UserScope(s)
        """
        return [UserScope(**cast(dict, s)) for s in self.get(path='me/permissions').data]

    def find_connected_page(
        self,
        page_id: int,
        instagram_account_id: Optional[int] = None,
        limit: Optional[int] = CONNECTED_PAGES_DEFAULT_LIMIT,
    ) -> Optional[ConnectedPage]:
        """
        Find a Page connected to a User by either Page ID and / or Instagram Account ID
        :param page_id: The Page ID to match
        :param instagram_account_id: Optional Instagram Account ID to match
        :param limit: Number of partial pages to return
        :return: Optional ConnectedPage partial
        """
        return first_true(
            (
                ConnectedPage.from_source_data(cast(dict, p))
                for p in self._get_paginated_results(
                    'me/accounts', params={'fields': CONNECTED_PAGES_FIELDS, 'limit': limit}
                )
            ),
            lambda p: p.matches_id_set(page_id, instagram_account_id),
        )
