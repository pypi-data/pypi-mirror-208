"""Represents a create inbox response message."""

from marshmallow import EXCLUDE, fields

from .....messaging.agent_message import AgentMessage, AgentMessageSchema

from ..message_types import CREATE_INBOX_RESPONSE, PROTOCOL_PACKAGE

HANDLER_CLASS = f"{PROTOCOL_PACKAGE}.handlers.create_inbox_response_handler.CreateInboxResponseHandler"


class CreateInboxResponse(AgentMessage):
    """Represents response to create-inbox message"""

    class Meta:
        """CreateInboxResponse metadata."""

        handler_class = HANDLER_CLASS
        message_type = CREATE_INBOX_RESPONSE
        schema_class = "CreateInboxResponseSchema"

    def __init__(self, *, inbox_id: str = None, inbox_key: str = None, **kwargs):
        """
        Initialize create inbox message object.
        """
        super().__init__(**kwargs)
        self.inbox_id = inbox_id
        self.inbox_key = inbox_key


class CreateInboxResponseSchema(AgentMessageSchema):
    """CreateInboxResponseSchema message schema used in serialization/deserialization."""

    class Meta:
        """CreateInboxResponseSchema metadata."""

        model_class = CreateInboxResponse
        unknown = EXCLUDE

    inbox_id = fields.Str(data_key="InboxId")
    inbox_key = fields.Str(data_key="InboxKey")
