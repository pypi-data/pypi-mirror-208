from .....messaging.base_handler import (
    BaseHandler,
    BaseResponder,
    RequestContext,
)
from ..messages.fetch_data_agreement import FetchDataAgreementMessage
from ..manager import IGrantIOOperatorManager


class FetchDataAgreementMessageHandler(BaseHandler):

    async def handle(self, context: RequestContext, responder: BaseResponder):
        self._logger.debug(
            "FetchDataAgreementMessageHandler called with context %s", context)
        assert isinstance(context.message, FetchDataAgreementMessage)

        self._logger.info(
            "Received fetch data agreement message: %s",
            context.message.serialize(as_string=True)
        )

        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        reply = await igrantio_operator_mgr.fetch_data_agreement(context.message, context.message_receipt)

        await responder.send_reply(reply)
