"""Handler for incoming create inbox messages."""

import json

from .....messaging.base_handler import (
    BaseHandler,
    BaseResponder,
    RequestContext,
    HandlerException
)
from ..messages.create_inbox import CreateInbox
from ..manager import BasicRoutingManager


class CreateInboxHandler(BaseHandler):
    """Handler for incoming create inbox messages."""

    async def handle(self, context: RequestContext, responder: BaseResponder):
        """Message handler implementation."""
        self._logger.debug("CreateInboxHandler called with context %s", context)
        assert isinstance(context.message, CreateInbox)

        self._logger.info(
            "Received create inbox message: %s",
            context.message.serialize(as_string=True)
        )

        if not context.connection_ready:
            raise HandlerException("Cannot create inbox: no active connection")

        basic_routing_mgr = BasicRoutingManager(context=context)
        reply = await basic_routing_mgr.create_inbox()

        if reply:
            await responder.send_reply(reply)
