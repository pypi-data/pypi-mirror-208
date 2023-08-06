"""Basic routing manager classes for managing mediator functions."""


import uuid
from time import time
import json

from ....config.injection_context import InjectionContext
from ....core.error import BaseError
from ....wallet.base import BaseWallet
from ....wallet.indy import IndyWallet
from ....messaging.responder import BaseResponder
from ....storage.indy import IndyStorage
from ....storage.base import BaseStorage, StorageRecord
from .messages.create_inbox import CreateInbox
from .messages.add_route import AddRoute
from .messages.create_inbox_response import CreateInboxResponse
from .messages.get_inbox_items_response import InboxForwardMessageResult, GetInboxItemsResponse


INBOX_INFO_RECORD_TYPE = "inbox_info"
ROUTE_INFO_RECORD_TYPE = "route_info"


class BasicRoutingManagerError(BaseError):
    """Generic basic-routing error."""


class BasicRoutingManager:
    """Class for handling basic-routing functions."""

    def __init__(self, context: InjectionContext):
        """
        Initialize a BasicRoutingManager.

        Args:
            context: The context for this manager
        """
        self._context = context
        if not context:
            raise BasicRoutingManagerError("Missing request context")

    @property
    def context(self) -> InjectionContext:
        """
        Accessor for the current request context.

        Returns:
            The request context for this connection

        """
        return self._context

    async def create_inbox(self):

        inbox_creds = {}

        # Check if inbox_info record exists
        storage = await self.context.inject(BaseStorage)
        inbox_info_records = await storage.search_records(
            type_filter=INBOX_INFO_RECORD_TYPE,
            tag_query={
                "connection_id": self.context.connection_record.connection_id
            }
        ).fetch_all()

        if inbox_info_records:
            inbox_creds["name"] = inbox_info_records[0].tags.get("inbox_name")
            inbox_creds["key"] = inbox_info_records[0].tags.get("inbox_key")
        else:
            # Add inbox_info record
            inbox_creds["name"] = str(uuid.uuid4())
            inbox_creds["key"] = str(uuid.uuid4())

            inbox_info_tags = {
                "inbox_name": inbox_creds["name"],
                "inbox_key": inbox_creds["key"],
                "epoch":  str(int(time())),
                "connection_id": self.context.connection_record.connection_id
            }

            record = StorageRecord(
                INBOX_INFO_RECORD_TYPE, self.context.connection_record.connection_id, inbox_info_tags
            )
            await storage.add_record(record)

        # Create inbox wallet if not exists
        inbox = IndyWallet(config=inbox_creds)
        await inbox.open()
        await inbox.close()

        # create response DIDComm message
        response = CreateInboxResponse(
            inbox_id=inbox_creds.get("name"),
            inbox_key=inbox_creds.get("key")
        )

        return response

    async def send_create_inbox(self, connection_id: str):

        request = CreateInbox()

        responder: BaseResponder = await self._context.inject(
            BaseResponder, required=False
        )
        if responder:
            await responder.send(request, connection_id=connection_id)

    async def add_route_message(self, routedestination: str = None):
        # Check route info record exists for the routedestination provided
        storage = await self.context.inject(BaseStorage)
        route_info_records = await storage.search_records(
            type_filter=ROUTE_INFO_RECORD_TYPE,
            tag_query={
                "connection_id": self.context.connection_record.connection_id,
                "routedestination": routedestination
            }
        ).fetch_all()

        if not route_info_records:
            # Create new route info record
            route_info_tags = {
                "routedestination": routedestination,
                "epoch":  str(int(time())),
                "connection_id": self.context.connection_record.connection_id
            }

            record = StorageRecord(
                ROUTE_INFO_RECORD_TYPE, self.context.connection_record.connection_id, route_info_tags
            )
            await storage.add_record(record)

    async def send_add_route_message(self, connection_id: str):

        request = AddRoute(routedestination="testroutekey")

        responder: BaseResponder = await self._context.inject(
            BaseResponder, required=False
        )
        if responder:
            await responder.send(request, connection_id=connection_id)

    async def get_inbox_items(self):
        inbox_creds = {}

        # Check if inbox_info record exists
        storage = await self.context.inject(BaseStorage)
        inbox_info_records = await storage.search_records(
            type_filter=INBOX_INFO_RECORD_TYPE,
            tag_query={
                "connection_id": self.context.connection_record.connection_id
            }
        ).fetch_all()

        if not inbox_info_records:
            return None

        inbox_creds["name"] = inbox_info_records[0].tags.get("inbox_name")
        inbox_creds["key"] = inbox_info_records[0].tags.get("inbox_key")

        inbox = IndyWallet(config=inbox_creds)
        await inbox.open()

        inbox_storage = IndyStorage(inbox)
        inbox_messages = await inbox_storage.search_records(
            type_filter="inbox-message",
            tag_query={}
        ).fetch_all()

        inbox_items_list = []

        for inbox_message in inbox_messages:

            print("\n\n\n")
            print(inbox_message.value)
            print(json.loads(inbox_message.value))
            print("\n\n\n")

            inbox_items_list.append(
                InboxForwardMessageResult(
                    json.loads(inbox_message.value),
                    timestamp=int(inbox_message.tags.get("epoch")),
                    _id=inbox_message.tags.get("id"),
                    _type=""
                )
            )

        await inbox.close()

        response = GetInboxItemsResponse(items=inbox_items_list)
        return response

    async def delete_inbox_items_fn(self):
        inbox_creds = {}

        # Check if inbox_info record exists
        storage = await self.context.inject(BaseStorage)
        inbox_info_records = await storage.search_records(
            type_filter=INBOX_INFO_RECORD_TYPE,
            tag_query={
                "connection_id": self.context.connection_record.connection_id
            }
        ).fetch_all()

        if not inbox_info_records:
            return None

        inbox_creds["name"] = inbox_info_records[0].tags.get("inbox_name")
        inbox_creds["key"] = inbox_info_records[0].tags.get("inbox_key")

        inbox = IndyWallet(config=inbox_creds)
        await inbox.open()

        inbox_storage = IndyStorage(inbox)
        inbox_messages = await inbox_storage.search_records(
            type_filter="inbox-message",
            tag_query={}
        ).fetch_all()

        for inbox_message in inbox_messages:
            await inbox_storage.delete_record(inbox_message)

        await inbox.close()
