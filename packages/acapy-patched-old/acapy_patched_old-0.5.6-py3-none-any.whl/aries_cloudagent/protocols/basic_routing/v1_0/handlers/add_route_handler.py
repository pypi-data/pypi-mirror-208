"""Handler for incoming add route messages."""

import json

from .....messaging.base_handler import (
    BaseHandler,
    BaseResponder,
    RequestContext,
    HandlerException
)
from ..messages.add_route import AddRoute
from ..manager import BasicRoutingManager


class AddRouteHandler(BaseHandler):
    """Handler for incoming add route messages."""

    async def handle(self, context: RequestContext, responder: BaseResponder):
        """Message handler implementation."""
        self._logger.debug("AddRouteHandler called with context %s", context)
        assert isinstance(context.message, AddRoute)

        self._logger.info(
            "Received add route message: %s",
            context.message.serialize(as_string=True)
        )

        if not context.connection_ready:
            raise HandlerException("Cannot add route: no active connection")

        basic_routing_mgr = BasicRoutingManager(context=context)
        await basic_routing_mgr.add_route_message(context.message.routedestination)

        if context.message_receipt.direct_response_requested and context.message_receipt.direct_response_mode:
            await responder.send_reply(b'{}')
