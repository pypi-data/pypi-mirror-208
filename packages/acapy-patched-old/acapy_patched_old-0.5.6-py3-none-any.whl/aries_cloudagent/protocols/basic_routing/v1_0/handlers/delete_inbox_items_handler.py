
import json

from .....messaging.base_handler import (
    BaseHandler,
    BaseResponder,
    RequestContext,
    HandlerException
)
from ..messages.delete_inbox_items import DeleteInboxItems
from ..manager import BasicRoutingManager


class DeleteInboxItemsHandler(BaseHandler):

    async def handle(self, context: RequestContext, responder: BaseResponder):
        self._logger.debug("DeleteInboxItemsHandler called with context %s", context)
        assert isinstance(context.message, DeleteInboxItems)

        self._logger.info(
            "Received delete inbox items message: %s",
            context.message.serialize(as_string=True)
        )

        if not context.connection_ready:
            raise HandlerException("Cannot delete inbox items: no active connection")

        basic_routing_mgr = BasicRoutingManager(context=context)
        await basic_routing_mgr.delete_inbox_items_fn()

        if context.message_receipt.direct_response_requested and context.message_receipt.direct_response_mode:
            await responder.send_reply(b'{}')
