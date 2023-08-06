from .....messaging.base_handler import (
    BaseHandler,
    BaseResponder,
    RequestContext,
)

from ..messages.fetch_data_agreement_response import FetchDataAgreementResponseMessage


class FetchDataAgreementResponseMessageHandler(BaseHandler):

    async def handle(self, context: RequestContext, responder: BaseResponder):
        self._logger.debug(
            "FetchDataAgreementResponseMessageHandler called with context %s", context)
        assert isinstance(context.message, FetchDataAgreementResponseMessage)

        self._logger.info(
            "Received fetch data agreement response message: %s",
            context.message.serialize(as_string=True)
        )
