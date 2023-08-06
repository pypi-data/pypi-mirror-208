"""Handler for incoming create inbox response messages."""

import json

from .....messaging.base_handler import (
    BaseHandler,
    BaseResponder,
    RequestContext,
    HandlerException
)
from ..messages.create_inbox_response import CreateInboxResponse


class CreateInboxResponseHandler(BaseHandler):
    """Handler for incoming create inbox response messages."""

    async def handle(self, context: RequestContext, responder: BaseResponder):
        """Message handler implementation."""
        self._logger.debug("CreateInboxResponseHandler called with context %s", context)
        assert isinstance(context.message, CreateInboxResponse)

        self._logger.info(
            "Received create inbox response message: %s",
            context.message.serialize(as_string=True)
        )

