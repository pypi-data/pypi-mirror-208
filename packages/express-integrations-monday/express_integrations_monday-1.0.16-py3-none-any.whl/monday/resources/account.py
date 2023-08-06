from monday.query_joins import (
    get_account_query,
    get_app_subscription_query,
    get_apps_monetization_supported_query,
    get_self_query,
)
from monday.resources.base import BaseResource


class AccountResource(BaseResource):
    def __init__(self, token):
        super().__init__(token)

    def get_apps_monetization_supported(self):
        query = get_apps_monetization_supported_query()
        return self.client.execute(query)

    def get_app_subscription(self):
        query = get_app_subscription_query()
        return self.client.execute(query)

    def get_account(self):
        query = get_account_query()
        return self.client.execute(query)

    def get_self(self):
        query = get_self_query()
        return self.client.execute(query)
