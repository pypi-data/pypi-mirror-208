"""Message type identifiers for Routing."""

from ...didcomm_prefix import DIDCommPrefix

# Message types
CREATE_INBOX = f"basic-routing/1.0/create-inbox"
CREATE_INBOX_RESPONSE = f"basic-routing/1.0/create-inbox-response"

ADD_ROUTE = f"basic-routing/1.0/add-route"

GET_INBOX_ITEMS = f"basic-routing/1.0/get-inbox-items"
GET_INBOX_ITEMS_RESPONSE = f"basic-routing/1.0/get-inbox-items-response"

DELETE_INBOX_ITEMS = f"basic-routing/1.0/delete-inbox-items"
INBOX_ITEM = f"basic-routing/1.0/inbox-item"

ADD_DEVICE_INFO = f"basic-routing/1.0/add-device-info"

PROTOCOL_PACKAGE = "aries_cloudagent.protocols.basic_routing.v1_0"

MESSAGE_TYPES = DIDCommPrefix.qualify_all(
    {
        CREATE_INBOX: f"{PROTOCOL_PACKAGE}.messages.create_inbox.CreateInbox",
        CREATE_INBOX_RESPONSE: (
            f"{PROTOCOL_PACKAGE}.messages.create_inbox_response.CreateInboxResponse"
        ),
        ADD_ROUTE: (
            f"{PROTOCOL_PACKAGE}.messages.add_route.AddRoute"
        ),
        GET_INBOX_ITEMS: (
            f"{PROTOCOL_PACKAGE}.messages.get_inbox_items.GetInboxItems"
        ),
        GET_INBOX_ITEMS_RESPONSE: (
            f"{PROTOCOL_PACKAGE}.messages.get_inbox_items_response.GetInboxItemsResponse"
        ),
        DELETE_INBOX_ITEMS: (
            f"{PROTOCOL_PACKAGE}.messages.delete_inbox_items.DeleteInboxItems"
        ),
        INBOX_ITEM: (
            f"{PROTOCOL_PACKAGE}.messages.route_update_response.RouteUpdateResponse"
        ),
        ADD_DEVICE_INFO: (
            f"{PROTOCOL_PACKAGE}.messages.route_update_response.RouteUpdateResponse"
        ),
    }
)
