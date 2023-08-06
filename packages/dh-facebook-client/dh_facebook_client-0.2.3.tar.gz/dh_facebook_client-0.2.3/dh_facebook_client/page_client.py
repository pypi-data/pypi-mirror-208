from typing import cast

from .client import GraphAPIClient
from .dataclasses import PageWebhookSubscription


class PageClient(GraphAPIClient):
    """
    Extends GraphAPIClient to include helpers for common Page-based functionality
    """

    def get_subscribed_apps(self) -> list[PageWebhookSubscription]:
        """
        Fetches a list of webhook subscriptions the page is subscribed to
        :return: List of parsed webhook subscription states
        """
        result = self.get('me/subscribed_apps')
        return [PageWebhookSubscription(**cast(dict, s)) for s in result.data]

    def subscribe_to_webhook(self, fields: list[str]) -> bool:
        """
        Subscribes a Page to the Meta webhook for the supplied fields
        :param fields: Webhook fields to subscribe the page to
        :return: Bool value indicating if the subscription was established
        """
        result = self.post('me/subscribed_apps', data={'subscribed_fields': ','.join(fields)})
        return cast(dict, result.data).get('success', False)
