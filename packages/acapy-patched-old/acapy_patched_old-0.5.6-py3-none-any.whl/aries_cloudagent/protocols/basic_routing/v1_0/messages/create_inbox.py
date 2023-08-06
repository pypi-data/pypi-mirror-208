"""Represents a create inbox message."""

from marshmallow import EXCLUDE, fields

from .....messaging.agent_message import AgentMessage, AgentMessageSchema

from ..message_types import CREATE_INBOX, PROTOCOL_PACKAGE

HANDLER_CLASS = f"{PROTOCOL_PACKAGE}.handlers.create_inbox_handler.CreateInboxHandler"


class CreateInbox(AgentMessage):
    """Represents a request to create an inbox."""

    class Meta:
        """CreateInbox metadata."""

        handler_class = HANDLER_CLASS
        message_type = CREATE_INBOX
        schema_class = "CreateInboxSchema"

    def __init__(self, **kwargs):
        """
        Initialize create inbox message object.
        """
        super().__init__(**kwargs)


class CreateInboxSchema(AgentMessageSchema):
    """CreateInbox message schema used in serialization/deserialization."""

    class Meta:
        """CreateInboxSchema metadata."""

        model_class = CreateInbox
        unknown = EXCLUDE
