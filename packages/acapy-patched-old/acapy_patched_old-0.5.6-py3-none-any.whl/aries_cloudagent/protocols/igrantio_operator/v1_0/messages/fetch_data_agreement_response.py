
from marshmallow import EXCLUDE, fields

from .....messaging.agent_message import AgentMessage, AgentMessageSchema

from ..message_types import FETCH_DATA_AGREEMENT_RESPONSE, PROTOCOL_PACKAGE

HANDLER_CLASS = f"{PROTOCOL_PACKAGE}.handlers.fetch_data_agreement_response_handler.FetchDataAgreementResponseMessageHandler"


class FetchDataAgreementResponseMessage(AgentMessage):

    class Meta:
        handler_class = HANDLER_CLASS
        message_type = FETCH_DATA_AGREEMENT_RESPONSE
        schema_class = "FetchDataAgreementResponseMessageSchema"

    def __init__(self, *, org_details, purpose_details, **kwargs):
        super().__init__(**kwargs)
        self.org_details = org_details
        self.purpose_details = purpose_details


class FetchDataAgreementResponseMessageSchema(AgentMessageSchema):
    class Meta:

        model_class = FetchDataAgreementResponseMessage
        unknown = EXCLUDE

    org_details = fields.Dict()
    purpose_details = fields.Dict()
