"""
monday.client
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2022 by Express Integrations.
:license: Apache2, see LICENSE for more details.
"""

from .__version__ import __version__
from .resources import (
    BoardResource,
    ComplexityResource,
    GroupResource,
    ItemResource,
    NotificationResource,
    TagResource,
    UpdateResource,
    UserResource,
    WorkspaceResource,
    WebhooksResource,
    AccountResource,
    BaseResource
)


class MondayClient:
    def __init__(self, token):
        """
        :param token: API Token for the new :class:`BaseResource` object.
        """
        self.items = ItemResource(token=token)
        self.updates = UpdateResource(token=token)
        self.tags = TagResource(token=token)
        self.boards = BoardResource(token=token)
        self.users = UserResource(token=token)
        self.groups = GroupResource(token=token)
        self.complexity = ComplexityResource(token=token)
        self.workspaces = WorkspaceResource(token=token)
        self.notifications = NotificationResource(token=token)
        self.base = BaseResource(api_key=token)
        self.webhooks = WebhooksResource(token=token)
        self.account = AccountResource(token = token)

    def __str__(self):
        return f'MondayClient {__version__}'

    def __repr__(self):
        return f'MondayClient {__version__}'
