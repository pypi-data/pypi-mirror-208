from monday.resources.base import BaseResource
from monday.query_joins import get_users_query, get_teams_query


class UserResource(BaseResource):
    def __init__(self, token):
        super().__init__(token)

    def fetch_users(self, **kwargs):
        query = get_users_query(**kwargs)
        return self.client.execute(query)

    def get_teams(self):
        query = get_teams_query()
        return self.client.execute(query)
