from monday.query_joins import (
    create_board_by_workspace_query,
    get_board_items_by_id_query, get_board_items_query,
    get_boards_by_id_query,
    get_boards_query,
    get_columns_by_board_query,
    get_board_activity_query, get_paginated_board_items_query,
)
from monday.resources.base import BaseResource


class BoardResource(BaseResource):
    def __init__(self, token):
        super().__init__(token)

    def fetch_boards(self, **kwargs):
        query = get_boards_query(**kwargs)
        return self.client.execute(query)

    def fetch_boards_by_id(self, board_ids):
        query = get_boards_by_id_query(board_ids)
        return self.client.execute(query)

    def fetch_items_by_board_id(self, board_ids):
        query = get_board_items_query(board_ids)
        return self.client.execute(query)

    def fetch_paginated_items_by_board_id(self, board_ids, page, limit):
        query = get_paginated_board_items_query(board_ids, page, limit)
        return self.client.execute(query)

    def fetch_items_by_board_id_and_item_id(self, board_ids, item_id):
        query = get_board_items_by_id_query(board_ids, item_id)
        return self.client.execute(query)

    def fetch_columns_by_board_id(self, board_ids):
        query = get_columns_by_board_query(board_ids)
        return self.client.execute(query)

    def create_board(self, board_name, board_kind, workspace_id):
        query = create_board_by_workspace_query(board_name, board_kind, workspace_id)
        return self.client.execute(query)

    def get_board_activity(self, board_id, from_date, to_date, page, limit):
        query = get_board_activity_query(board_id, from_date, to_date, page, limit)
        return self.client.execute(query)
