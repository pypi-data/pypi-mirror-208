import json
from typing import Optional

from .utils import monday_json_stringify


# ITEM RESOURCE QUERIES
def mutate_item_query(
    board_id, group_id, item_name, column_values,
    create_labels_if_missing
):
    # Monday does not allow passing through non-JSON null values here,
    # so if you choose not to specify column values, need to set column_values to empty object.
    column_values = column_values if column_values else {}

    query = '''
    mutation {
        create_item (
            board_id: %s,
            group_id: "%s",
            item_name: "%s",
            column_values: %s,
            create_labels_if_missing: %s
        ) {
            id
        }
    }''' % (board_id, group_id, item_name, monday_json_stringify(column_values),
            str(create_labels_if_missing).lower())

    return query


def mutate_subitem_query(
    parent_item_id, subitem_name, column_values,
    create_labels_if_missing
):
    column_values = column_values if column_values else {}

    query = '''
    mutation {
        create_subitem (
            parent_item_id: %s,
            item_name: "%s",
            column_values: %s,
            create_labels_if_missing: %s
        ) {
            id,
            name,
            column_values {
                id,
                title
                text
            },
            board {
                id,
                name
            }
        }
    }''' % (parent_item_id, subitem_name, monday_json_stringify(column_values),
            str(create_labels_if_missing).lower())
    return query


def get_item_query(board_id, column_id, value):
    query = '''
    query {
        items_by_column_values(
            board_id: %s,
            column_id: %s,
            column_value: "%s"
        ) {
            id
            name
            updates {
                id
                body
            }
            group {
                id
                title
            }
            column_values {
                id
                title
                text
                value
            }
        }
    }''' % (board_id, column_id, value)

    return query


def get_item_by_id_query(ids):
    query = '''
    query {
        items (ids: %s) {
            id,
            name,
            group {
                id
                title
            }
            column_values {
                id,
                title,
                text,
                value,
                type
            }
        }
    }''' % ids

    return query


def update_item_query(board_id, item_id, column_id, value):
    query = '''
    mutation {
        change_column_value(
            board_id: %s,
            item_id: %s,
            column_id: %s,
            value: %s
        ) {
            id
            name
            column_values {
                id
                text
                value
            }
        }
    }''' % (board_id, item_id, column_id, monday_json_stringify(value))

    return query


def delete_item_query(item_id):
    query = '''
    mutation {
        delete_item (item_id: %s)
        {
            id
        }
    }''' % item_id
    return query


def update_multiple_column_values_query(board_id, item_id, column_values, create_labels_if_missing):
    query = '''
    mutation {
        change_multiple_column_values (
            board_id: %s,
            item_id: %s,
            column_values: %s,
            create_labels_if_missing: %s
        ) {
            id
            name
            column_values {
              id
              text
            }
        }
    }''' % (board_id, item_id, monday_json_stringify(column_values), str(create_labels_if_missing).lower())

    return query


def add_file_to_column_query(item_id, column_id):
    query = '''
    mutation ($file: File!) {
        add_file_to_column (
            file: $file,
            item_id: %s,
            column_id: %s
        ) {
            id
        }
    }''' % (item_id, column_id)
    return query


# UPDATE RESOURCE QUERIES
def create_update_query(item_id, update_value):
    query = '''
    mutation {
        create_update(
            item_id: %s,
            body: %s
        ) {
            id
        }
    }''' % (item_id, json.dumps(update_value))

    return query


def get_updates_for_item_query(board, item, limit):
    query = '''
    query {
        boards (ids: %s) {
            items (ids: %s) {
                updates (limit: %s) {
                    id,
                    body,
                    created_at,
                    updated_at,
                    creator {
                        id,
                        name,
                        email
                    },
                    assets {
                        id,
                        name,
                        url,
                        file_extension,
                        file_size                  
                    },
                    replies {
                        id,
                        body,
                        creator{
                            id,
                            name,
                            email
                        },
                        created_at,
                        updated_at
                    }
                }
            }
        }
    }''' % (board, item, limit)

    return query


def get_update_query(limit, page):
    query = '''
    query {
        updates (
            limit: %s,
            page: %s
        ) {
            id,
            body
        }
    }
    ''' % (limit, page if page else 1)

    return query


# TAG RESOURCE QUERIES
def get_tags_query(tags):
    if tags is None:
        tags = []

    query = '''
    query {
        tags (ids: %s) {
            name,
            color,
            id
        }
    }
    ''' % tags

    return query


# BOARD RESOURCE QUERIES
def get_board_items_query(board_id):
    query = '''
    query {
        boards(ids: %s) {
            name
            items {
                group {
                    id
                    title
                }
                id
                name
                column_values {
                  id
                  title
                  text
                  type
                  value
                }
            }
        }
    }
    ''' % (
        board_id if not isinstance(board_id, list)
        else [int(i) for i in board_id]
    )

    return query


def get_board_items_by_id_query(board_id, item_id):
    query = '''
    query {
        boards(ids: %s) {
            name
            items (ids: %s) {
                group {
                    id
                    title
                }
                id
                name
                column_values {
                  id
                  title
                  text
                  type
                  value
                }
            }
        }
    }
    ''' % (
        board_id if not isinstance(board_id, list)
        else [int(i) for i in board_id],
        item_id
    )

    return query


def get_paginated_board_items_query(board_id, page, limit):
    query = '''
    query {
        boards(ids: %s) {
            name
            items (page: %s, limit: %s) {
                group {
                    id
                    title
                }
                id
                name
                column_values {
                  id
                  title
                  text
                  type
                  value
                }
            }
        }
    }
    ''' % (
        board_id if not isinstance(board_id, list)
        else [int(i) for i in board_id],
        page,
        limit
    )

    return query


def get_boards_query(**kwargs):
    query = '''
    query {
        boards (%s) {
            id
            name
            permissions
            tags {
              id
              name
            }
            groups {
                id
                title
            }
            columns {
                id
                title
                type
            }
        }
    }
    ''' % ', '.join(["%s: %s" % (arg, kwargs.get(arg)) for arg in kwargs])
    return query


def get_board_ids_query(**kwargs):
    query = '''
    query {
        boards (%s) {
            id
            name
        }
    }
    ''' % ', '.join(["%s: %s" % (arg, kwargs.get(arg)) for arg in kwargs])
    return query


def get_boards_by_id_query(board_ids):
    return '''
    query {
        boards (ids: %s) {
            id
            name
            permissions
            tags {
              id
              name
            }
            groups {
                id
                title
            }
            columns {
                id
                title
                type
                settings_str
            }
        }
    }
    ''' % board_ids


def get_columns_by_board_query(board_ids):
    return '''
    query {
        boards(ids: %s) {
            id
            name
            groups {
                id
                title
            }
            columns {
                title
                id
                type
                settings_str
             }
        }
    }
    ''' % board_ids


def create_board_by_workspace_query(board_name, board_kind, workspace_id = None):
    workspace_query = f'workspace_id: {workspace_id}' if workspace_id else ''
    query = '''
    mutation {
        create_board (board_name:"%s", board_kind: %s, %s) {
            id
        }
    }
    ''' % (board_name, board_kind, workspace_query)
    return query


# USER RESOURCE QUERIES
def get_users_query(**kwargs):
    query = '''
    query {
        users (%s) {
            id,
            url,
            name,
            email,
            phone,
            teams {
              id
            },
            title,
            enabled,
            birthday,
            is_admin,
            is_guest,
            location,
            join_date,
            created_at,
            is_pending,
            is_verified,
            country_code,
            is_view_only,
            mobile_phone,
            time_zone_identifier
        }
    }
    ''' % ', '.join(["%s: %s" % (arg, kwargs.get(arg)) for arg in kwargs])
    return query


# GROUP RESOURCE QUERIES
def get_groups_by_board_query(board_ids):
    query = '''
    query {
        boards(ids: %s) {
            groups {
                id
                title
                archived
                deleted
                color
            }
        }
    }
    ''' % board_ids
    return query


def get_items_by_group_query(board_id, group_id):
    query = '''
    query {
        boards(ids: %s) {
            groups(ids: "%s") {
                id
                title
                items {
                    id
                    name
                }
            }
        }
    }
    ''' % (board_id, group_id)
    return query


def create_group_query(board_id, group_name):
    query = '''
    mutation {
        create_group(board_id: %s, group_name: "%s")
        {
            id
        }
    }
    ''' % (board_id, group_name)
    return query


def duplicate_group_query(board_id, group_id):
    query = '''
    mutation {
        duplicate_group(board_id: %s, group_id: "%s")
        {
            id
        }
    }
    ''' % (board_id, group_id)
    return query


def archive_group_query(board_id, group_id):
    query = '''
    mutation {
        archive_group(board_id: %s, group_id: "%s")
        {
            id
            archived
        }
    }
    ''' % (board_id, group_id)
    return query


def delete_group_query(board_id, group_id):
    query = '''
    mutation {
        delete_group(board_id: %s, group_id: "%s")
        {
            id
            deleted
        }
    }
    ''' % (board_id, group_id)
    return query


def get_complexity_query():
    query = '''
    query {
        complexity {
            after,
            reset_in_x_seconds
        }
    }
    '''

    return query


def get_workspaces_query():
    query = '''
    query {
        workspaces {
            id
            name
            kind
            description
        }
    }
    '''
    return query


def create_workspace_query(name, kind, description = ""):
    query = '''
    mutation {
        create_workspace (name:"%s", kind: %s, description: "%s") {
            id
            description
        }
    }
    ''' % (name, kind, description)
    return query


def add_users_to_workspace_query(workspace_id, user_ids, kind):
    query = '''
    mutation {
        add_users_to_workspace (workspace_id: %s, user_ids: %s, kind: %s) {
            id
        }
    }
    ''' % (workspace_id, user_ids, kind)
    return query


def delete_users_from_workspace_query(workspace_id, user_ids):
    query = '''
    mutation {
        add_users_to_workspace (workspace_id: %s, user_ids: %s) {
            id
        }
    }
    ''' % (workspace_id, user_ids)
    return query


def add_teams_to_workspace_query(workspace_id, team_ids):
    query = '''
    mutation {
        add_teams_to_workspace (workspace_id: %s, team_ids: %s) {
            id
        }
    }
    ''' % (workspace_id, team_ids)
    return query


def delete_teams_from_workspace_query(workspace_id, team_ids):
    query = '''
    mutation {
        delete_teams_from_workspace (workspace_id: %s, team_ids: %s) {
            id
        }
    }
    ''' % (workspace_id, team_ids)
    return query


def create_notification_query(user_id, target_id, text, target_type):
    query = '''
    mutation {
        create_notification (user_id: %s, target_id: %s, text: "%s", target_type: %s) {
            text
            user_id
            target_id
            target_type
        }
    }
    ''' % (user_id, target_id, text, target_type)
    # Target type may be: Project/Post
    return query


def get_self_query():
    query = '''
    query {
        me {
            email,
            name
        }
    }
    '''

    return query


def get_apps_monetization_supported_query():
    query = '''
    query {
        apps_monetization_status {
            is_supported
        }
    }
    '''

    return query


def get_app_subscription_query():
    query = '''
    query {
        app_subscription {
            plan_id,
            is_trial,
            renewal_date,
            days_left,
            billing_period
        }
    }
    '''

    return query


def get_account_query():
    query = '''
    query {
        account {
            slug,
            name
        }
    }
    '''

    return query


def get_teams_query():
    query = '''
    query {
        teams {
            id,
            picture_url,
            name,
            users {
              id
            }
          }
    }
    '''

    return query


def get_board_activity_query(board_id, from_date, to_date, page, limit):
    query = '''
    query {
        boards(ids: %s) {
            activity_logs(from: "%s", to: "%s", page: %s, limit: %s) {
                id,
                entity,
                event,
                user_id,
                account_id
                data,
                created_at
            }
        }
    }
    ''' % (board_id, from_date, to_date, page, limit)
    return query


def create_webhook_query(board_id, url, event, column_id: Optional[str]):
    column_config = f', config: "{{\\"columnId\\": \\"{column_id}\\"}}"' if column_id else ''
    query = rf"""
    mutation {{
        create_webhook (board_id:{board_id}, url: "{url}", event: {event}{column_config}) {{
            id
            board_id
        }}
    }}
    """
    return query


def delete_webhook_query(webhook_id):
    query = '''
    mutation {
        delete_webhook (id:%s) {
            id
            board_id
        }
    }
    ''' % webhook_id
    return query
