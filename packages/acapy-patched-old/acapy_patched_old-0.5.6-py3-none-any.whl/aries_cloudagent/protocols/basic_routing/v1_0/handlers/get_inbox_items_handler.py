from .....messaging.base_handler import (
    BaseHandler,
    BaseResponder,
    RequestContext,
    HandlerException
)
from ..messages.get_inbox_items import GetInboxItems
from ..manager import BasicRoutingManager


class GetInboxItemsHandler(BaseHandler):

    async def handle(self, context: RequestContext, responder: BaseResponder):
        self._logger.debug("GetInboxItemsHandler called with context %s", context)
        assert isinstance(context.message, GetInboxItems)

        self._logger.info(
            "Received get inbox items message: %s",
            context.message.serialize(as_string=True)
        )

        if not context.connection_ready:
            raise HandlerException("Cannot fetch inbox items: no active connection")

        basic_routing_mgr = BasicRoutingManager(context=context)
        reply = await basic_routing_mgr.get_inbox_items()

        if reply:
            await responder.send_reply(reply)
