from typing import Optional

from .base import BaseResource
from ..query_joins import (create_webhook_query, delete_webhook_query)


class WebhooksResource(BaseResource):
    def __init__(self, token):
        super().__init__(token)

    def create_webhook(self, board_id, url, event, column_id: Optional[str]):
        query = create_webhook_query(board_id, url, event, column_id)
        return self.client.execute(query)
    
    def delete_webhook(self, webhook_id):
        query = delete_webhook_query(webhook_id)
        return self.client.execute(query)
    