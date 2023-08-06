"""Represents a get inbox items response message."""

from .....messaging.models.base import BaseModel, BaseModelSchema
from marshmallow import fields
from marshmallow import EXCLUDE, fields

from .....messaging.agent_message import AgentMessage, AgentMessageSchema

from ..message_types import GET_INBOX_ITEMS_RESPONSE, PROTOCOL_PACKAGE

HANDLER_CLASS = f"{PROTOCOL_PACKAGE}.handlers.get_inbox_items_response_handler.GetInboxItemsResponseHandler"


"""A list data certificate types inner object."""


class InboxForwardMessageResult(BaseModel):
    class Meta:
        schema_class = "ListDataCertificateTypesResultSchema"

    def __init__(
        self,
        data,
        timestamp: int,
        _id: str,
        _type: str,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.data = data
        self.timestamp = timestamp
        self._id = _id
        self._type = _type


class InboxForwardMessageResultSchema(BaseModelSchema):
    class Meta:
        model_class = InboxForwardMessageResult

    data = fields.Dict(data_key="Data")
    timestamp = fields.Integer(data_key="Timestamp")
    _id = fields.Str(data_key="@id")
    _type = fields.Str(data_key="@type")


class GetInboxItemsResponse(AgentMessage):
    class Meta:
        handler_class = HANDLER_CLASS
        message_type = GET_INBOX_ITEMS_RESPONSE
        schema_class = "GetInboxItemsResponseSchema"

    def __init__(self, *, items, **kwargs):
        super().__init__(**kwargs)
        self.items = items


class GetInboxItemsResponseSchema(AgentMessageSchema):
    class Meta:

        model_class = GetInboxItemsResponse
        unknown = EXCLUDE

    items = fields.List(fields.Nested(
        InboxForwardMessageResultSchema()), data_key="Items")
