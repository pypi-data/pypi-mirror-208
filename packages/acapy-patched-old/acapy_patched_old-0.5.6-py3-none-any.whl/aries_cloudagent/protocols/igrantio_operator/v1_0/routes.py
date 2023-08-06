"""iGrant.io operator handling admin routes."""

import aiohttp
import os
import io
from marshmallow import fields
from aiohttp import web
from aiohttp_apispec import (
    docs,
    match_info_schema,
    querystring_schema,
    response_schema,
    request_schema
)
import aiohttp_jinja2
import jinja2
import qrcode
import base64

from .valid import IGrantIOAPIKeyJWS
from .manager import IGrantIOOperatorManager
from ....messaging.models.openapi import OpenAPISchema
from ....messaging.valid import UUIDFour, IndyDID
from ....storage.error import StorageNotFoundError
from ....connections.models.connection_record import ConnectionRecord
from ...present_proof.v1_0.routes import IndyProofRequestSchema
from ....indy.util import generate_pr_nonce

from pathlib import Path

here = Path(__file__).resolve().parent


class QRIdMatchInfoSchema(OpenAPISchema):
    """Path parameters and validators for request taking QR id."""

    qr_id = fields.Str(
        description="QR identifier", required=True, example=UUIDFour.EXAMPLE
    )


class FetchDataAgreementMatchInfoSchema(OpenAPISchema):

    conn_id = fields.Str(
        description="Connection identifier", required=True, example=UUIDFour.EXAMPLE
    )

    exchange_template_id = fields.Str(
        description="Exchange template ID", required=True)

    exchange_mode = fields.Str(
        description="Exchange mode <issue/verify>", required=True)


class AutoDataExchangeIdMatchInfoSchema(OpenAPISchema):
    """Path parameters and validators for request taking auto data exchange id."""

    auto_data_ex_id = fields.Str(
        description="Automated data exchange identifier", required=True, example=UUIDFour.EXAMPLE
    )


class ConnIdMatchInfoSchema(OpenAPISchema):
    """Path parameters and validators for request taking connection id."""

    conn_id = fields.Str(
        description="Connection identifier", required=True, example=UUIDFour.EXAMPLE
    )


class InformExistingConnectionQueryStringSchema(OpenAPISchema):
    """Parameters and validators for inform existing connection query string."""

    their_did = fields.Str(
        description="Existing pairwise Their DID",
        required=True
    )


class OperatorConfigurationQueryStringSchema(OpenAPISchema):
    """Parameters and validators for operator configuration query string."""

    operator_endpoint = fields.Str(
        description="Operator endpoint",
        required=True,
        example="https://api.igrant.io"
    )

    api_key = fields.Str(
        description="iGrant.io operator API key",
        required=True,
        example=IGrantIOAPIKeyJWS.EXAMPLE
    )

    org_id = fields.Str(
        description="Organization ID",
        required=True,
        example=UUIDFour.EXAMPLE
    )


class OperatorConfigurationResultSchema(OpenAPISchema):
    """Result schema for operator configuration."""

    api_key = fields.Str(
        description="iGrant.io operator API key", example=IGrantIOAPIKeyJWS.EXAMPLE
    )

    org_id = fields.Str(
        description="Organization ID",
        required=True,
        example=UUIDFour.EXAMPLE
    )


class FetchMultiConnectionsInfoResultSchema(OpenAPISchema):
    """Fetch multi connection info results schema"""

    existing_connection_id = fields.Str(
        required=True,
        description="Existing connection ID",
        example=UUIDFour.EXAMPLE,
    )
    my_did = fields.Str(
        required=True, description="My DID", example=IndyDID.EXAMPLE
    )
    connection_status = fields.Str(
        description="Existing connection status",
        example="available/notavailable"
    )
    connection_id = fields.Str(
        description="New connection ID",
        example=UUIDFour.EXAMPLE,
    )


class ResolveQRShortLinkDataResultSchema(OpenAPISchema):
    """Resolve QR short link data result schema"""

    invitation_url = fields.Str(
        required=True,
        description="Invitation URL",
        example="http://localhost:5010?c_i=eyJAdHlwZSI6ICJkaWQ6c292OkJ6Q2JzTlloTXJqSGlxWkRUVUFTSGc7c3BlYy9jb25uZWN0aW9ucy8xLjAvaW52aXRhdGlvbiIsICJAaWQiOiAiY2IyY2ZiM2ItMDM1NS00NjZmLTg5YWQtNmRiNGM5MDY5Y2ZkIiwgInJlY2lwaWVudEtleXMiOiBbIkViUkJDNWZ5WVI2OXFrdlFyZ3JTUVdGVms1bkJEVkRpS3RZdUhmamFBMUM2Il0sICJzZXJ2aWNlRW5kcG9pbnQiOiAiaHR0cDovL2xvY2FsaG9zdDo1MDEwIiwgImxhYmVsIjogIlRlc3QgQ2VudGVyIiwgImltYWdlX3VybCI6ICJodHRwczovL2RlbW8tYXBpLmlncmFudC5pby92MS9vcmdhbml6YXRpb25zLzVmNTIzOGRkYzY3MDAxMDAwMTAwZjlkOS9pbWFnZS82MDIzYTYyNzQ2YmM3ZjAwMDE0ZWQ2NjMvd2ViIn0=",
    )


class AutomatedDataExchangeDetailRecordResultSchema(OpenAPISchema):
    """Automated data exchange detail record result schema"""

    auto_data_ex_id = fields.Str(
        required=True,
        description="Automated data exchange template ID",
        example=UUIDFour.EXAMPLE
    )

    presentation_request = fields.Nested(IndyProofRequestSchema())


class QRAutomatedDataExchangeRecordResultSchema(OpenAPISchema):
    """QR automated data exchange record result schema"""

    auto_data_ex_id = fields.Str(
        required=True,
        description="Automated data exchange template ID",
        example=UUIDFour.EXAMPLE
    )

    qr_id = fields.Str(
        required=True,
        description="QR ID",
        example=UUIDFour.EXAMPLE
    )

    qr_data = fields.Str(
        required=True,
        description="QR data (URL) ",
        example="http://localhost:5010?qr_p=eyJpbnZpdGF0aW9uX3VybCI6ICJodHRwOi8vbG9jYWxob3N0OjUwMTA_Y19pPWV5SkFkSGx3WlNJNklDSmthV1E2YzI5Mk9rSjZRMkp6VGxsb1RYSnFTR2x4V2tSVVZVRlRTR2M3YzNCbFl5OWpiMjV1WldOMGFXOXVjeTh4TGpBdmFXNTJhWFJoZEdsdmJpSXNJQ0pBYVdRaU9pQWlOVGc1WWpoa09ERXRZekU0TVMwME1UY3pMV0V4T0RndE4yWTRObU16TTJRNE5XRmhJaXdnSW5KbFkybHdhV1Z1ZEV0bGVYTWlPaUJiSWpOT2QwVnJOMmt5V1hsSFJFWkRaRnBPUm1Oek9IaHBTREowU0dWSGQyWnJXVlpTV0hwSVdFNWhVREZTSWwwc0lDSnpaWEoyYVdObFJXNWtjRzlwYm5RaU9pQWlhSFIwY0RvdkwyeHZZMkZzYUc5emREbzFNREV3SWl3Z0lteGhZbVZzSWpvZ0lsUmxjM1FnUTJWdWRHVnlJaXdnSW1sdFlXZGxYM1Z5YkNJNklDSm9kSFJ3Y3pvdkwyUmxiVzh0WVhCcExtbG5jbUZ1ZEM1cGJ5OTJNUzl2Y21kaGJtbDZZWFJwYjI1ekx6Vm1OVEl6T0dSa1l6WTNNREF4TURBd01UQXdaamxrT1M5cGJXRm5aUzgyTURJellUWXlOelEyWW1NM1pqQXdNREUwWldRMk5qTXZkMlZpSW4wPSIsICJwcm9vZl9yZXF1ZXN0IjogeyJuYW1lIjogIkNPVklELTE5IHRlc3QgdmVyaWZpY2F0aW9uIiwgInZlcnNpb24iOiAiMS4wIiwgInJlcXVlc3RlZF9hdHRyaWJ1dGVzIjogeyJhZGRpdGlvbmFsUHJvcDEiOiB7Im5hbWUiOiAiVGVzdCBkYXRlIiwgInJlc3RyaWN0aW9ucyI6IFtdfSwgImFkZGl0aW9uYWxQcm9wMiI6IHsibmFtZSI6ICJQYXRpZW50IGFnZSIsICJyZXN0cmljdGlvbnMiOiBbXX0sICJhZGRpdGlvbmFsUHJvcDMiOiB7Im5hbWUiOiAiUGF0aWVudCBuYW1lIiwgInJlc3RyaWN0aW9ucyI6IFtdfX0sICJyZXF1ZXN0ZWRfcHJlZGljYXRlcyI6IHt9LCAibm9uY2UiOiAiMzAzMDU5NzIyMDQ5MTI4MTg4MDI2Njc2In19"
    )

    connection_id = fields.Str(
        required=True,
        description="Connection ID",
        example=UUIDFour.EXAMPLE
    )

    nonce = fields.Str(
        required=True,
        description="Random nonce",
        example="303059722049128188026676"
    )


class ResolveQRAutomatedDataExchangeRecordResultSchema(OpenAPISchema):
    """Resolve QR automated data exchange record result schema"""

    dataexchange_url = fields.Str(
        required=True,
        description="Data exchange (URL) ",
        example="http://localhost:5010?qr_p=eyJpbnZpdGF0aW9uX3VybCI6ICJodHRwOi8vbG9jYWxob3N0OjUwMTA_Y19pPWV5SkFkSGx3WlNJNklDSmthV1E2YzI5Mk9rSjZRMkp6VGxsb1RYSnFTR2x4V2tSVVZVRlRTR2M3YzNCbFl5OWpiMjV1WldOMGFXOXVjeTh4TGpBdmFXNTJhWFJoZEdsdmJpSXNJQ0pBYVdRaU9pQWlOVGc1WWpoa09ERXRZekU0TVMwME1UY3pMV0V4T0RndE4yWTRObU16TTJRNE5XRmhJaXdnSW5KbFkybHdhV1Z1ZEV0bGVYTWlPaUJiSWpOT2QwVnJOMmt5V1hsSFJFWkRaRnBPUm1Oek9IaHBTREowU0dWSGQyWnJXVlpTV0hwSVdFNWhVREZTSWwwc0lDSnpaWEoyYVdObFJXNWtjRzlwYm5RaU9pQWlhSFIwY0RvdkwyeHZZMkZzYUc5emREbzFNREV3SWl3Z0lteGhZbVZzSWpvZ0lsUmxjM1FnUTJWdWRHVnlJaXdnSW1sdFlXZGxYM1Z5YkNJNklDSm9kSFJ3Y3pvdkwyUmxiVzh0WVhCcExtbG5jbUZ1ZEM1cGJ5OTJNUzl2Y21kaGJtbDZZWFJwYjI1ekx6Vm1OVEl6T0dSa1l6WTNNREF4TURBd01UQXdaamxrT1M5cGJXRm5aUzgyTURJellUWXlOelEyWW1NM1pqQXdNREUwWldRMk5qTXZkMlZpSW4wPSIsICJwcm9vZl9yZXF1ZXN0IjogeyJuYW1lIjogIkNPVklELTE5IHRlc3QgdmVyaWZpY2F0aW9uIiwgInZlcnNpb24iOiAiMS4wIiwgInJlcXVlc3RlZF9hdHRyaWJ1dGVzIjogeyJhZGRpdGlvbmFsUHJvcDEiOiB7Im5hbWUiOiAiVGVzdCBkYXRlIiwgInJlc3RyaWN0aW9ucyI6IFtdfSwgImFkZGl0aW9uYWxQcm9wMiI6IHsibmFtZSI6ICJQYXRpZW50IGFnZSIsICJyZXN0cmljdGlvbnMiOiBbXX0sICJhZGRpdGlvbmFsUHJvcDMiOiB7Im5hbWUiOiAiUGF0aWVudCBuYW1lIiwgInJlc3RyaWN0aW9ucyI6IFtdfX0sICJyZXF1ZXN0ZWRfcHJlZGljYXRlcyI6IHt9LCAibm9uY2UiOiAiMzAzMDU5NzIyMDQ5MTI4MTg4MDI2Njc2In19"
    )


@docs(
    tags=["igrantio_operator"],
    summary="Fetch iGrant.io operator configuration",
)
@response_schema(OperatorConfigurationResultSchema(), 200)
async def igrantio_operator_configuration(request: web.BaseRequest):
    """
    Request handler for fetching iGrant.io operator configuration.

    Args:
        request: aiohttp request object

    Returns:
        iGrant.io operator configuration response

    """

    context = request.app["request_context"]

    igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
    operator_configuration = await igrantio_operator_mgr.fetch_operator_configuration()

    if operator_configuration:
        result = {
            "api_key": operator_configuration.api_key,
            "org_id": operator_configuration.org_id,
            "operator_endpoint": operator_configuration.operator_endpoint
        }
    else:
        result = {
            "api_key": context.settings.get("igrantio_api_key"),
            "org_id": context.settings.get("igrantio_org_id"),
            "operator_endpoint": context.settings.get("igrantio_endpoint")
        }

    return web.json_response(result)


@docs(
    tags=["igrantio_operator"],
    summary="Configure iGrant.io operator",
)
@querystring_schema(OperatorConfigurationQueryStringSchema())
@response_schema(OperatorConfigurationResultSchema(), 200)
async def configure_igrantio_operator(request: web.BaseRequest):
    """
    Request handler for configuring igrantio operator

    Args:
        request: aiohttp request object

    Returns:
        The igrantio operator configuration details

    """
    context = request.app["request_context"]

    api_key = request.query.get("api_key")
    org_id = request.query.get("org_id")
    operator_endpoint = request.query.get("operator_endpoint")

    igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
    operator_configuration = await igrantio_operator_mgr.update_operator_configuration(
        api_key=api_key,
        org_id=org_id,
        operator_endpoint=operator_endpoint
    )

    result = {
        "api_key": operator_configuration.api_key,
        "org_id": operator_configuration.org_id,
        "operator_endpoint": operator_configuration.operator_endpoint
    }

    return web.json_response(result)


@docs(
    tags=["igrantio_operator"],
    summary="Fetch organization details from the operator",
)
async def fetch_organization_details(request: web.BaseRequest):
    """
    Request handler to fetch organization details

    Args:
        request: aiohttp request object

    Returns:
        Organization details

    """
    context = request.app["request_context"]

    igrantio_operator_mgr = IGrantIOOperatorManager(context=context)

    operator_configuration = {}
    operator_configuration = await igrantio_operator_mgr.fetch_operator_configuration()

    if not operator_configuration:
        operator_configuration = {
            "api_key": context.settings.get("igrantio_api_key"),
            "org_id": context.settings.get("igrantio_org_id"),
            "operator_endpoint": context.settings.get("igrantio_endpoint")
        }

    result = {}
    if operator_configuration:

        org_info_route = "/v1/organizations/{org_id}".format(
            org_id=operator_configuration["org_id"])

        headers = {'Authorization': 'ApiKey {}'.format(operator_configuration["api_key"])}

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(operator_configuration["operator_endpoint"] + org_info_route) as resp:
                if resp.status == 200:
                    resp_json = await resp.json()

                    exclude_keys = [
                        "BillingInfo",
                        "Admins",
                        "HlcSupport",
                        "DataRetention",
                        "Enabled",
                        "ID",
                        "Subs"
                    ]

                    for exclude_key in exclude_keys:
                        resp_json["Organization"].pop(exclude_key, None)

                    result = resp_json["Organization"]

    return web.json_response(result)


@docs(
    tags=["igrantio_operator"],
    summary="Sending message for listing available data certificate types that can be issued"
)
@match_info_schema(ConnIdMatchInfoSchema())
async def list_available_data_certificates_types(request: web.BaseRequest):
    """
    Request handle for listing available data certificate types that can be issued

    Args:
        request: aiohttp request object
    """
    context = request.app["request_context"]
    connection_id = request.match_info["conn_id"]

    try:
        record: ConnectionRecord = await ConnectionRecord.retrieve_by_id(context, connection_id)
        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        await igrantio_operator_mgr.list_data_certificate_types_request(connection_id=record.connection_id)
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response({"msg": "DIDComm message send to the connected agent."})


@docs(
    tags=["igrantio_operator"],
    summary="Sending message for fetching organization info"
)
@match_info_schema(ConnIdMatchInfoSchema())
async def send_organization_info_request(request: web.BaseRequest):
    """
    Request handle for fetching organization info

    Args:
        request: aiohttp request object
    """
    context = request.app["request_context"]
    connection_id = request.match_info["conn_id"]

    try:
        record: ConnectionRecord = await ConnectionRecord.retrieve_by_id(context, connection_id)
        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        await igrantio_operator_mgr.send_organization_info_request(connection_id=record.connection_id)
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response({"msg": "DIDComm message send to the connected agent."})


@docs(
    tags=["igrantio_operator"],
    summary="Sending message to inform existing connection"
)
@querystring_schema(InformExistingConnectionQueryStringSchema())
@match_info_schema(ConnIdMatchInfoSchema())
async def send_multiconnections_info(request: web.BaseRequest):
    """
    Request handle to inform existing connection

    Args:
        request: aiohttp request object
    """
    context = request.app["request_context"]
    connection_id = request.match_info["conn_id"]

    their_did = request.query.get("their_did")

    try:
        record: ConnectionRecord = await ConnectionRecord.retrieve_by_id(context, connection_id)
        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        await igrantio_operator_mgr.send_org_multiple_connections_info_message(connection_id=record.connection_id, theirdid=their_did)
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response({"msg": "DIDComm message send to the connected agent."})


@docs(
    tags=["igrantio_operator"],
    summary="Fetch multi connections record for a connection ID if available"
)
@match_info_schema(ConnIdMatchInfoSchema())
@response_schema(FetchMultiConnectionsInfoResultSchema(), 200)
async def fetch_multiconnections_info(request: web.BaseRequest):
    """
    Request handle to fetch multi connection record for a connection ID

    Args:
        request: aiohttp request object
    """
    context = request.app["request_context"]
    connection_id = request.match_info["conn_id"]

    result = {}

    try:
        record: ConnectionRecord = await ConnectionRecord.retrieve_by_id(context, connection_id)
        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        result = await igrantio_operator_mgr.fetch_org_multiple_connections_record_by_connection_id(connection_id=record.connection_id)
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response(result)


@docs(
    tags=["igrantio_operator"],
    summary="Resolve connection invitation short link"
)
@match_info_schema(ConnIdMatchInfoSchema())
@response_schema(ResolveQRShortLinkDataResultSchema(), 200)
async def resolve_qr_short_link_data(request: web.BaseRequest):
    """
    Request handle to resolve connection invitation short link

    Args:
        request: aiohttp request object
    """
    context = request.app["request_context"]
    connection_id = request.match_info["conn_id"]

    result = {
        "invitation_url": ""
    }

    try:
        record: ConnectionRecord = await ConnectionRecord.retrieve_by_id(context, connection_id)
        if record.state == ConnectionRecord.STATE_INVITATION:
            igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
            result["invitation_url"] = await igrantio_operator_mgr.fetch_org_connection_invitation_json(connection_id=record.connection_id)
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response(result)


async def get_deep_link_connection_as_json(request: web.BaseRequest):

    conn_id = request.match_info["conn_id"]
    context = request.app["request_context"]

    connection_qr_resolve_route_path = request.app.router['resolve_qr_short_link_data'].url_for(
        conn_id=conn_id)

    connection_qr_url = context.settings.get(
        "default_endpoint").replace("agent/", "admin") + str(connection_qr_resolve_route_path)

    firebase_web_api_key = os.environ.get(
        "firebase_web_api_key", "AIzaSyBOZtiOwrqPBe42rWeh0dNaOj2RvxtyoUU")
    payload = {
        "dynamicLinkInfo": {
            "domainUriPrefix": "https://datawallet.page.link",
            "link": connection_qr_url,
            "androidInfo": {
                "androidPackageName": "io.igrant.mobileagent"
            },
            "iosInfo": {
                "iosBundleId": "io.iGrant.DataWallet",
                "iosAppStoreId": "1546551969"
            }
        },
        "suffix": {
            "option": "UNGUESSABLE"
        }
    }

    resp_json = {}

    async with aiohttp.ClientSession() as session:
        async with session.post("https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key=" + firebase_web_api_key, json=payload) as resp:
            if resp.status == 200:
                resp_json = await resp.json()

    context = {}

    return web.json_response(resp_json)


async def get_deep_link_connection(request: web.BaseRequest):

    conn_id = request.match_info["conn_id"]
    context = request.app["request_context"]

    connection_qr_resolve_route_path = request.app.router['resolve_qr_short_link_data'].url_for(
        conn_id=conn_id)

    connection_qr_url = context.settings.get(
        "default_endpoint").replace("agent/", "admin") + str(connection_qr_resolve_route_path)

    firebase_web_api_key = os.environ.get(
        "firebase_web_api_key", "AIzaSyBOZtiOwrqPBe42rWeh0dNaOj2RvxtyoUU")
    payload = {
        "dynamicLinkInfo": {
            "domainUriPrefix": "https://datawallet.page.link",
            "link": connection_qr_url,
            "androidInfo": {
                "androidPackageName": "io.igrant.mobileagent"
            },
            "iosInfo": {
                "iosBundleId": "io.iGrant.DataWallet",
                "iosAppStoreId": "1546551969"
            }
        },
        "suffix": {
            "option": "UNGUESSABLE"
        }
    }

    resp_json = None

    async with aiohttp.ClientSession() as session:
        async with session.post("https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key=" + firebase_web_api_key, json=payload) as resp:
            if resp.status == 200:
                resp_json = await resp.json()

    context = {}
    if not resp_json:
        context = {'error': True}
    else:

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(connection_qr_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

        context = {'qr_image_str': img_str, 'short_link': resp_json["shortLink"]}

    response = aiohttp_jinja2.render_template('qr.html',
                                              request,
                                              context)
    return response


@docs(
    tags=["igrantio_operator"],
    summary="Create automated data exchange record"
)
@request_schema(IndyProofRequestSchema())
@response_schema(AutomatedDataExchangeDetailRecordResultSchema(), 200)
async def create_automated_dataexchange_record(request: web.BaseRequest):
    """
    Request handler to create automated data exchange record

    Args:
        request: aiohttp request object

    """
    context = request.app["request_context"]

    indy_proof_request = await request.json()

    if not indy_proof_request.get("nonce"):
        indy_proof_request["nonce"] = await generate_pr_nonce()

    result = {}

    try:
        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        result = await igrantio_operator_mgr.create_automated_data_exchange_record(
            presentation_request=indy_proof_request
        )
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response(result)


@docs(
    tags=["igrantio_operator"],
    summary="Update automated data exchange record"
)
@request_schema(IndyProofRequestSchema())
@match_info_schema(AutoDataExchangeIdMatchInfoSchema())
@response_schema(AutomatedDataExchangeDetailRecordResultSchema(), 200)
async def update_automated_dataexchange_record(request: web.BaseRequest):
    """
    Request handler to update automated data exchange record

    Args:
        request: aiohttp request object

    """
    context = request.app["request_context"]
    auto_data_ex_id = request.match_info["auto_data_ex_id"]

    indy_proof_request = await request.json()

    if not indy_proof_request.get("nonce"):
        indy_proof_request["nonce"] = await generate_pr_nonce()

    result = {}

    try:
        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        result = await igrantio_operator_mgr.update_automated_data_exchange_record(
            auto_data_ex_id=auto_data_ex_id,
            presentation_request=indy_proof_request
        )

        if not result:
            raise web.HTTPInternalServerError(
                reason="Failed to update automated data exchange record")

    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response(result)


@docs(
    tags=["igrantio_operator"],
    summary="Get automated data exchange record"
)
@match_info_schema(AutoDataExchangeIdMatchInfoSchema())
@response_schema(AutomatedDataExchangeDetailRecordResultSchema(), 200)
async def get_automated_dataexchange_record(request: web.BaseRequest):
    """
    Request handler to get automated data exchange record

    Args:
        request: aiohttp request object

    """
    context = request.app["request_context"]
    auto_data_ex_id = request.match_info["auto_data_ex_id"]

    result = {}

    try:
        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        result = await igrantio_operator_mgr.get_automated_data_exchange_record(auto_data_ex_id=auto_data_ex_id)
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response(result)


@docs(
    tags=["igrantio_operator"],
    summary="Delete automated data exchange record",
    responses={
        204: {
            "description": "Deleted automated data exchange record"
        },
        500: {
            "description": "Failed to delete automated data exchange record"
        },
        404: {
            "description": "Automated data exchange record not found"
        }
    }
)
@match_info_schema(AutoDataExchangeIdMatchInfoSchema())
async def delete_automated_dataexchange_record(request: web.BaseRequest):
    """
    Request handler to delete automated data exchange record

    Args:
        request: aiohttp request object

    """
    context = request.app["request_context"]
    auto_data_ex_id = request.match_info["auto_data_ex_id"]

    result = {}

    try:
        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        result = await igrantio_operator_mgr.delete_automated_data_exchange_record(auto_data_ex_id=auto_data_ex_id)

        if not result:
            raise web.HTTPInternalServerError(
                reason="Failed to delete automated data exchange record")

    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response(status=web.HTTPNoContent.status_code)


@docs(
    tags=["igrantio_operator"],
    summary="List automated data exchange records"
)
@response_schema(AutomatedDataExchangeDetailRecordResultSchema(many=True), 200)
async def list_automated_dataexchange_record(request: web.BaseRequest):
    """
    Request handler to list automated data exchange records

    Args:
        request: aiohttp request object

    """
    context = request.app["request_context"]

    result = []

    try:
        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        result = await igrantio_operator_mgr.list_automated_data_exchange_record()
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response(result)


# TODO : Create automated data exchange QR code data.


@docs(
    tags=["igrantio_operator"],
    summary="Create automated QR data exchange record"
)
@match_info_schema(AutoDataExchangeIdMatchInfoSchema())
@response_schema(QRAutomatedDataExchangeRecordResultSchema(), 200)
async def create_qr_automated_dataexchange_record(request: web.BaseRequest):
    """
    Request handler to create qr automated data exchange record

    Args:
        request: aiohttp request object

    """
    context = request.app["request_context"]
    auto_data_ex_id = request.match_info["auto_data_ex_id"]

    result = {}

    try:
        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        result = await igrantio_operator_mgr.create_qr_automated_data_exchange_record(auto_data_ex_id=auto_data_ex_id)
        if not result:
            raise web.HTTPInternalServerError(
                reason="Failed to create QR automated data exchange record")
        
        dataexchange_qr_resolve_route_path = request.app.router['get_qr_automated_dataexchange_record'].url_for(
            qr_id=result.get("qr_id", ""))

        connection_qr_url = context.settings.get(
            "default_endpoint").replace("agent/", "admin") + str(dataexchange_qr_resolve_route_path)

        firebase_web_api_key = os.environ.get(
            "firebase_web_api_key", "AIzaSyBOZtiOwrqPBe42rWeh0dNaOj2RvxtyoUU")
        payload = {
            "dynamicLinkInfo": {
                "domainUriPrefix": "https://datawallet.page.link",
                "link": connection_qr_url,
                "androidInfo": {
                    "androidPackageName": "io.igrant.mobileagent"
                },
                "iosInfo": {
                    "iosBundleId": "io.iGrant.DataWallet",
                    "iosAppStoreId": "1546551969"
                }
            },
            "suffix": {
                "option": "UNGUESSABLE"
            }
        }

        resp_json = {}

        async with aiohttp.ClientSession() as session:
            async with session.post("https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key=" + firebase_web_api_key, json=payload) as resp:
                if resp.status == 200:
                    resp_json = await resp.json()
        
        if resp_json:
            result["qr_url"] = resp_json["shortLink"]
        else:
            result["qr_url"] = ""

    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response(result)


@docs(
    tags=["igrantio_operator"],
    summary="Generate QR code for automated data exchange"
)
@match_info_schema(AutoDataExchangeIdMatchInfoSchema())
async def generate_qr_automated_dataexchange(request: web.BaseRequest):
    """
    Request handler to create qr automated data exchange record

    Args:
        request: aiohttp request object

    """
    context = request.app["request_context"]
    auto_data_ex_id = request.match_info["auto_data_ex_id"]

    result = {}

    try:
        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        result = await igrantio_operator_mgr.create_qr_automated_data_exchange_record(auto_data_ex_id=auto_data_ex_id)
        if not result:
            raise web.HTTPInternalServerError(
                reason="Failed to create QR automated data exchange record")
        
        qr_id = result.get("qr_id", "")

        context = request.app["request_context"]

        dataexchange_qr_resolve_route_path = request.app.router['get_qr_automated_dataexchange_record'].url_for(
            qr_id=qr_id)

        connection_qr_url = context.settings.get(
            "default_endpoint").replace("agent/", "admin") + str(dataexchange_qr_resolve_route_path)


        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(connection_qr_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")


    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.Response(status=200, body=buffer.getvalue(), content_type="image/jpeg")


# TODO : Delete automated data exchange QR code data.

@docs(
    tags=["igrantio_operator"],
    summary="Delete QR automated data exchange record",
    responses={
        204: {
            "description": "Deleted QR automated data exchange record"
        },
        500: {
            "description": "Failed to delete QR automated data exchange record"
        },
        404: {
            "description": "QR automated data exchange record not found"
        }
    }
)
@match_info_schema(QRIdMatchInfoSchema())
async def delete_qr_automated_dataexchange_record(request: web.BaseRequest):
    """
    Request handler to delete QR automated data exchange record

    Args:
        request: aiohttp request object

    """
    context = request.app["request_context"]
    qr_id = request.match_info["qr_id"]

    result = {}

    try:
        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        result = await igrantio_operator_mgr.delete_qr_automated_data_exchange_record(qr_id=qr_id)

        if not result:
            raise web.HTTPInternalServerError(
                reason="Failed to delete QR automated data exchange record")
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response(status=web.HTTPNoContent.status_code)

# TODO : List automated data exchange QR code data.


@docs(
    tags=["igrantio_operator"],
    summary="List automated QR data exchange records"
)
@match_info_schema(AutoDataExchangeIdMatchInfoSchema())
@response_schema(QRAutomatedDataExchangeRecordResultSchema(many=True), 200)
async def list_qr_automated_dataexchange_record(request: web.BaseRequest):
    """
    Request handler to list QR automated data exchange records

    Args:
        request: aiohttp request object

    """
    context = request.app["request_context"]
    auto_data_ex_id = request.match_info["auto_data_ex_id"]

    result = []

    try:
        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        result = await igrantio_operator_mgr.list_qr_automated_data_exchange_record(
            auto_data_ex_id=auto_data_ex_id
        )
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response(result)


# TODO : Get automated data exchange QR code data. (resolve)

@docs(
    tags=["igrantio_operator"],
    summary="Resolve automated data exchange QR short link"
)
@match_info_schema(QRIdMatchInfoSchema())
@response_schema(ResolveQRAutomatedDataExchangeRecordResultSchema(), 200)
async def get_qr_automated_dataexchange_record(request: web.BaseRequest):
    """
    Request handler to resolve automated data exchange QR short link

    Args:
        request: aiohttp request object

    """
    context = request.app["request_context"]
    qr_id = request.match_info["qr_id"]

    result = {}

    try:
        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        result = await igrantio_operator_mgr.get_qr_automated_data_exchange_record(qr_id=qr_id)
        if not result:
            raise web.HTTPInternalServerError(
                reason="Failed to fetch QR automated data exchange record")

    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response(result)


async def get_deep_link_dataexchange_as_json(request: web.BaseRequest):

    qr_id = request.match_info["qr_id"]
    context = request.app["request_context"]

    dataexchange_qr_resolve_route_path = request.app.router['get_qr_automated_dataexchange_record'].url_for(
        qr_id=qr_id)

    connection_qr_url = context.settings.get(
        "default_endpoint").replace("agent/", "admin") + str(dataexchange_qr_resolve_route_path)

    firebase_web_api_key = os.environ.get(
        "firebase_web_api_key", "AIzaSyBOZtiOwrqPBe42rWeh0dNaOj2RvxtyoUU")
    payload = {
        "dynamicLinkInfo": {
            "domainUriPrefix": "https://datawallet.page.link",
            "link": connection_qr_url,
            "androidInfo": {
                "androidPackageName": "io.igrant.mobileagent"
            },
            "iosInfo": {
                "iosBundleId": "io.iGrant.DataWallet",
                "iosAppStoreId": "1546551969"
            }
        },
        "suffix": {
            "option": "UNGUESSABLE"
        }
    }

    resp_json = {}

    async with aiohttp.ClientSession() as session:
        async with session.post("https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key=" + firebase_web_api_key, json=payload) as resp:
            if resp.status == 200:
                resp_json = await resp.json()

    return web.json_response(resp_json)


async def get_deep_link_dataexchange(request: web.BaseRequest):

    qr_id = request.match_info["qr_id"]
    context = request.app["request_context"]

    dataexchange_qr_resolve_route_path = request.app.router['get_qr_automated_dataexchange_record'].url_for(
        qr_id=qr_id)

    connection_qr_url = context.settings.get(
        "default_endpoint").replace("agent/", "admin") + str(dataexchange_qr_resolve_route_path)

    firebase_web_api_key = os.environ.get(
        "firebase_web_api_key", "AIzaSyBOZtiOwrqPBe42rWeh0dNaOj2RvxtyoUU")
    payload = {
        "dynamicLinkInfo": {
            "domainUriPrefix": "https://datawallet.page.link",
            "link": connection_qr_url,
            "androidInfo": {
                "androidPackageName": "io.igrant.mobileagent"
            },
            "iosInfo": {
                "iosBundleId": "io.iGrant.DataWallet",
                "iosAppStoreId": "1546551969"
            }
        },
        "suffix": {
            "option": "UNGUESSABLE"
        }
    }

    resp_json = None

    async with aiohttp.ClientSession() as session:
        async with session.post("https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key=" + firebase_web_api_key, json=payload) as resp:
            if resp.status == 200:
                resp_json = await resp.json()

    context = {}
    if not resp_json:
        context = {'error': True}
    else:

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(connection_qr_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

        context = {'qr_image_str': img_str, 'short_link': resp_json["shortLink"]}

    response = aiohttp_jinja2.render_template('qr.html',
                                              request,
                                              context)
    return response


@docs(
    tags=["igrantio_operator"],
    summary="Sending message for fetching data agreements"
)
@match_info_schema(FetchDataAgreementMatchInfoSchema())
async def send_fetch_data_agreement_message(request: web.BaseRequest):
    context = request.app["request_context"]
    connection_id = request.match_info["conn_id"]
    exchange_template_id = request.match_info["exchange_template_id"]
    exchange_mode = request.match_info["exchange_mode"]

    try:
        record: ConnectionRecord = await ConnectionRecord.retrieve_by_id(context, connection_id)
        igrantio_operator_mgr = IGrantIOOperatorManager(context=context)
        await igrantio_operator_mgr.send_fetch_data_agreement_request_message(connection_id=record.connection_id,
                                                                              exchange_template_id=exchange_template_id,
                                                                              exchange_mode=exchange_mode)
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response({"msg": "DIDComm message send to the connected agent."})
# TODO : Notify deleted connection
# TODO : Make changes to connection delete API to notify the connection that connection has expired


async def register(app: web.Application):
    """Register routes."""

    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader(str(here) + "/templates"))
    app['static_root_url'] = '/static'

    app.add_routes(
        [
            # web.get("/igrantio-operator/operator-configuration",
            #         igrantio_operator_configuration, allow_head=False),
            # web.post("/igrantio-operator/operator-configuration",
            #          configure_igrantio_operator),
            # web.get("/igrantio-operator/organization-info",
            #         fetch_organization_details, allow_head=False),
            # web.post("/igrantio-operator/connections/{conn_id}/list-data-certificate-types",
            #          list_available_data_certificates_types),
            # web.post("/igrantio-operator/connections/{conn_id}/organization-info",
            #          send_organization_info_request),
            web.get("/igrantio-operator/connections/{conn_id}/org-multiple-connections",
                    fetch_multiconnections_info,
                    allow_head=False,),
            # web.post("/igrantio-operator/connections/{conn_id}/org-multiple-connections",
            #          send_multiconnections_info),
            web.post("/igrantio-operator/connection/qr-link/{conn_id}",
                     resolve_qr_short_link_data, name="resolve_qr_short_link_data"),
            web.get("/igrantio-operator/connection/qr-link/{conn_id}",
                    get_deep_link_connection),
            web.get("/igrantio-operator/connection/deep-link/{conn_id}",
                    get_deep_link_connection_as_json),
            web.post("/igrantio-operator/connections/{conn_id}/fetch-data-agreement/{exchange_template_id}/exchange_type/{exchange_mode}",
                     send_fetch_data_agreement_message),

            # Data exchange template related route

            web.post("/igrantio-operator/data-exchange",
                     create_automated_dataexchange_record),
            web.get("/igrantio-operator/data-exchange/{auto_data_ex_id}",
                    get_automated_dataexchange_record, allow_head=False,),
            web.delete("/igrantio-operator/data-exchange/{auto_data_ex_id}",
                       delete_automated_dataexchange_record),
            web.get("/igrantio-operator/data-exchange",
                    list_automated_dataexchange_record, allow_head=False,),

            # Data exchange QR related routes

            web.delete("/igrantio-operator/data-exchange/qr/{qr_id}",
                       delete_qr_automated_dataexchange_record),
            web.post("/igrantio-operator/data-exchange/qr/{auto_data_ex_id}",
                     create_qr_automated_dataexchange_record),
            web.post("/igrantio-operator/data-exchange/qr/{auto_data_ex_id}/generate",
                     generate_qr_automated_dataexchange),
            web.get("/igrantio-operator/data-exchange/qr/{auto_data_ex_id}/list",
                    list_qr_automated_dataexchange_record, allow_head=False,),
            web.post("/igrantio-operator/data-exchange/qr-link/{qr_id}",
                     get_qr_automated_dataexchange_record, name="get_qr_automated_dataexchange_record"),
            web.get("/igrantio-operator/data-exchange/qr-link/{qr_id}",
                    get_deep_link_dataexchange),
            web.get("/igrantio-operator/data-exchange/deep-link/{qr_id}",
                    get_deep_link_dataexchange_as_json),

        ]
    )


def post_process_routes(app: web.Application):
    """Amend swagger API."""

    # Add top-level tags description
    if "tags" not in app._state["swagger_dict"]:
        app._state["swagger_dict"]["tags"] = []
    app._state["swagger_dict"]["tags"].append(
        {
            "name": "igrantio_operator",
            "description": "iGrant.io operator management",
        }
    )
