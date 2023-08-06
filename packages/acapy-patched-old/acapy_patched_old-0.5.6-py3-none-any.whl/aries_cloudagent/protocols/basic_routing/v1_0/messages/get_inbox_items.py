"""Represents a get inbox items message."""

from marshmallow import EXCLUDE, fields

from .....messaging.agent_message import AgentMessage, AgentMessageSchema

from ..message_types import GET_INBOX_ITEMS, PROTOCOL_PACKAGE

HANDLER_CLASS = f"{PROTOCOL_PACKAGE}.handlers.get_inbox_items_handler.GetInboxItemsHandler"


class GetInboxItems(AgentMessage):

    class Meta:

        handler_class = HANDLER_CLASS
        message_type = GET_INBOX_ITEMS
        schema_class = "GetInboxItemsSchema"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class GetInboxItemsSchema(AgentMessageSchema):
    class Meta:

        model_class = GetInboxItems
        unknown = EXCLUDE
