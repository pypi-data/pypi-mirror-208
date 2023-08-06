"""Organization multiple connection message handler."""


from .....messaging.base_handler import (
    BaseHandler,
    BaseResponder,
    RequestContext,
)
from ..messages.problem_report import ProblemReport, ProblemReportReason
from ..messages.org_multiple_connections import OrgMultipleConnectionsMessage
from ..manager import IGrantIOOperatorManager


class OrgMultipleConnectionsHandler(BaseHandler):
    """Message handler class for organization multiple connection messages."""

    async def handle(self, context: RequestContext, responder: BaseResponder):
        """
        Message handler logic for organization multiple connection messages.

        Args:
            context: request context
            responder: responder callback
        """
        self._logger.debug(
            "OrgMultipleConnectionsHandler called with context %s", context)
        assert isinstance(context.message, OrgMultipleConnectionsMessage)

        self._logger.info(
            "Received organization multiple connection message: %s",
            context.message.serialize(as_string=True)
        )

        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        await igrantio_operator_mgr.org_multiple_connections_record_status(context.message, context.message_receipt)
