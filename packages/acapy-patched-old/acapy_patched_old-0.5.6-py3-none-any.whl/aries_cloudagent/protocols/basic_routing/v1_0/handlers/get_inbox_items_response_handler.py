
from .....messaging.base_handler import (
    BaseHandler,
    BaseResponder,
    RequestContext
)
from ..messages.get_inbox_items_response import GetInboxItemsResponse


class GetInboxItemsResponseHandler(BaseHandler):

    async def handle(self, context: RequestContext, responder: BaseResponder):
        self._logger.debug("GetInboxItemsResponseHandler called with context %s", context)
        assert isinstance(context.message, GetInboxItemsResponse)

        self._logger.info(
            "Received get inbox items response message: %s",
            context.message.serialize(as_string=True)
        )
