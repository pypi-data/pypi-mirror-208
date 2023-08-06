
from marshmallow import EXCLUDE, fields

from .....messaging.agent_message import AgentMessage, AgentMessageSchema

from ..message_types import FETCH_DATA_AGREEMENT, PROTOCOL_PACKAGE

HANDLER_CLASS = f"{PROTOCOL_PACKAGE}.handlers.fetch_data_agreement_handler.FetchDataAgreementMessageHandler"


class FetchDataAgreementMessage(AgentMessage):

    class Meta:
        handler_class = HANDLER_CLASS
        message_type = FETCH_DATA_AGREEMENT
        schema_class = "FetchDataAgreementMessageSchema"

    def __init__(self, *, exchange_template_id, exchange_mode, **kwargs):
        super().__init__(**kwargs)
        self.exchange_template_id = exchange_template_id
        self.exchange_mode = exchange_mode


class FetchDataAgreementMessageSchema(AgentMessageSchema):
    class Meta:

        model_class = FetchDataAgreementMessage
        unknown = EXCLUDE

    exchange_template_id = fields.Str()
    exchange_mode = fields.Str()
