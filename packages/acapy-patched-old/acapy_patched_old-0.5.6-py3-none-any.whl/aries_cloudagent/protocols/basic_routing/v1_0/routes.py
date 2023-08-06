"""iGrant.io operator handling admin routes."""

import aiohttp
from marshmallow import fields
from aiohttp import web
from aiohttp_apispec import (
    docs,
    match_info_schema,
    querystring_schema,
    response_schema,
)

from .manager import BasicRoutingManager
from ....messaging.models.openapi import OpenAPISchema
from ....messaging.valid import UUIDFour
from ....storage.error import StorageNotFoundError
from ....connections.models.connection_record import ConnectionRecord


class ConnIdMatchInfoSchema(OpenAPISchema):
    """Path parameters and validators for request taking connection id."""

    conn_id = fields.Str(
        description="Connection identifier", required=True, example=UUIDFour.EXAMPLE
    )


@docs(
    tags=["basic-routing"],
    summary="Send message to create-inbox"
)
@match_info_schema(ConnIdMatchInfoSchema())
async def send_create_inbox_message(request: web.BaseRequest):
    """
    Request handle to send message to create-inbox

    Args:
        request: aiohttp request object
    """
    context = request.app["request_context"]
    connection_id = request.match_info["conn_id"]

    try:
        record: ConnectionRecord = await ConnectionRecord.retrieve_by_id(context, connection_id)
        basic_routing_mgr = BasicRoutingManager(context=context)
        await basic_routing_mgr.send_create_inbox(connection_id=record.connection_id)
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response({"msg": "DIDComm message send to the connected agent."})


@docs(
    tags=["basic-routing"],
    summary="Send message to add-route"
)
@match_info_schema(ConnIdMatchInfoSchema())
async def send_add_route_message(request: web.BaseRequest):
    """
    Request handle to send message to add-route

    Args:
        request: aiohttp request object
    """
    context = request.app["request_context"]
    connection_id = request.match_info["conn_id"]

    try:
        record: ConnectionRecord = await ConnectionRecord.retrieve_by_id(context, connection_id)
        basic_routing_mgr = BasicRoutingManager(context=context)
        await basic_routing_mgr.send_add_route_message(connection_id=record.connection_id)
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response({"msg": "DIDComm message send to the connected agent."})


async def register(app: web.Application):
    """Register routes."""

    app.add_routes(
        [
            web.post("/basic-routing/connections/{conn_id}/create-inbox",
                     send_create_inbox_message),
            web.post("/basic-routing/connections/{conn_id}/add-route",
                     send_add_route_message),
        ]
    )


def post_process_routes(app: web.Application):
    """Amend swagger API."""

    # Add top-level tags description
    if "tags" not in app._state["swagger_dict"]:
        app._state["swagger_dict"]["tags"] = []
    app._state["swagger_dict"]["tags"].append(
        {
            "name": "basic-routing",
            "description": "iGrant.io basic routing protocols",
        }
    )
