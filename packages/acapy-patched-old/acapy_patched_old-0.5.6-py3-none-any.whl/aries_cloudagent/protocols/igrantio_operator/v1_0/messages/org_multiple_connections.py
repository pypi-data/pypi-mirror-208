"""Organization multiple connections message."""

from marshmallow import EXCLUDE, fields

from .....messaging.agent_message import AgentMessage, AgentMessageSchema

from ..message_types import ORG_MULTIPLE_CONNECTIONS, PROTOCOL_PACKAGE

HANDLER_CLASS = f"{PROTOCOL_PACKAGE}.handlers.org_multiple_connections_handler.OrgMultipleConnectionsHandler"


class OrgMultipleConnectionsMessage(AgentMessage):
    """Class defining the structure of organization multiple connections message."""

    class Meta:
        """Organization multiple connections message metadata class."""

        handler_class = HANDLER_CLASS
        message_type = ORG_MULTIPLE_CONNECTIONS
        schema_class = "OrgMultipleConnectionsMessageSchema"

    def __init__(self, *, theirdid, **kwargs):
        """
        Initialize organization multiple connections message object.
        """
        super().__init__(**kwargs)
        self.theirdid = theirdid


class OrgMultipleConnectionsMessageSchema(AgentMessageSchema):
    """List organization multiple connections message schema class."""

    class Meta:
        """List organization multiple connections message schema metadata."""

        model_class = OrgMultipleConnectionsMessage
        unknown = EXCLUDE

    theirdid = fields.Str()
