"""Represents an add route message."""

from marshmallow import EXCLUDE, fields

from .....messaging.agent_message import AgentMessage, AgentMessageSchema

from ..message_types import ADD_ROUTE, PROTOCOL_PACKAGE

HANDLER_CLASS = f"{PROTOCOL_PACKAGE}.handlers.add_route_handler.AddRouteHandler"


class AddRoute(AgentMessage):
    """Represents a request to add a route"""

    class Meta:
        """CreateInbox metadata."""

        handler_class = HANDLER_CLASS
        message_type = ADD_ROUTE
        schema_class = "AddRouteSchema"

    def __init__(self, *, routedestination: str = None, **kwargs):
        """
        Initialize add route message object.
        """
        super().__init__(**kwargs)
        self.routedestination = routedestination


class AddRouteSchema(AgentMessageSchema):
    """AddRoute message schema used in serialization/deserialization."""

    class Meta:
        """AddRouteSchema metadata."""

        model_class = AddRoute
        unknown = EXCLUDE

    routedestination = fields.Str()
