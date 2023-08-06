"""iGrant.io operator manager classes for tracking and inspecting operator records."""


import logging
import json
import uuid
import aiohttp
import datetime
import base64

from .messages.inner.list_data_certificate_types_result import ListDataCertificateTypesResult
from .messages.list_data_certificate_types_response import ListDataCertificateTypesResponseMessage
from .messages.list_data_certificate_types import ListDataCertificateTypesMessage
from .messages.organization_info import OrganizationInfoMessage
from .messages.organization_info_response import OrganizationInfoResponseMessage
from .messages.inner.organization_privacy_dashboard import OrganizationPrivacyDashboard
from .models.igrantio_operator_configuration_record import IGrantIOOperatorConfigurationRecord
from ....storage.base import BaseStorage
from ....storage.error import StorageNotFoundError
from ....core.error import BaseError
from ....config.injection_context import InjectionContext
from ....messaging.responder import BaseResponder
from ....messaging.credential_definitions.util import CRED_DEF_SENT_RECORD_TYPE
from ....transport.inbound.receipt import MessageReceipt
from ....connections.models.connection_record import ConnectionRecord
from ...connections.v1_0.manager import ConnectionManagerError, ConnectionManager
from ....storage.base import BaseStorage, StorageRecord
from .messages.org_multiple_connections import OrgMultipleConnectionsMessage
from .messages.fetch_data_agreement_response import FetchDataAgreementResponseMessage
from .messages.fetch_data_agreement import FetchDataAgreementMessage
from ....indy.util import generate_pr_nonce
from ....messaging.models.base import BaseModelError


class IGrantIOOperatorManagerError(BaseError):
    """Generic iGrant.io operator manager error."""


class IGrantIOOperatorManager:
    """Class for handling iGrant.io operator messages"""

    OPERATOR_CONFIG_RECORD_TYPE = "igrantio_operator_configuration"
    ORG_MULTIPLE_CONNECTIONS_RECORD_TYPE = "org_multi_connections_info"
    ORG_AUTO_DATA_EXCHANGE_RECORD_TYPE = "org_auto_data_exchange_record"
    ORG_AUTO_DX_QR_RECORD_TYPE = "org_auto_dx_qr_record"

    def __init__(self,  context: InjectionContext):
        """
        Initialize a IGrantIOOperatorManager.

        Args:
            context: The context for this manager
        """
        self._context = context
        self._logger = logging.getLogger(__name__)

    @property
    def context(self) -> InjectionContext:
        """
        Accessor for the current injection context.

        Returns:
            The injection context for this iGrant.io operator manager

        """
        return self._context

    async def fetch_operator_configuration(self) -> IGrantIOOperatorConfigurationRecord:
        """
        Fetches operator configuration record

        Returns:
            An `IGrantIOOperatorConfigurationRecord` instance

        """
        igrantio_operator_configurations = None
        igrantio_operator_configuration = None

        try:
            igrantio_operator_configurations = await IGrantIOOperatorConfigurationRecord.query(
                self.context, {}, {}, {})

        except StorageNotFoundError:
            pass

        if not igrantio_operator_configurations:
            return None

        igrantio_operator_configuration = igrantio_operator_configurations[0]
        return igrantio_operator_configuration

    async def update_operator_configuration(self, api_key: str = None, org_id: str = None, operator_endpoint: str = None) -> IGrantIOOperatorConfigurationRecord:
        """
        Updates operator configuration record

        Organization admin configures iGrant.io operator for integrating MyData operator
        functionalities within the cloud agent.

        Args:
            api_key: iGrant.io operator API key

        Returns:
            An `IGrantIOOperatorConfigurationRecord` instance

        """
        igrantio_operator_configurations = None
        igrantio_operator_configuration = None

        if not api_key:
            raise IGrantIOOperatorManagerError("API key not provided")

        if not org_id:
            raise IGrantIOOperatorManagerError("Organization ID not provided")

        if not operator_endpoint:
            raise IGrantIOOperatorManagerError("Operator endpoint not provided")

        try:
            igrantio_operator_configurations = await IGrantIOOperatorConfigurationRecord.query(
                self.context, {}, {}, {})

        except StorageNotFoundError:
            pass

        if not igrantio_operator_configurations:
            igrantio_operator_configuration = IGrantIOOperatorConfigurationRecord(
                api_key=api_key, org_id=org_id, operator_endpoint=operator_endpoint
            )
        else:
            igrantio_operator_configuration = igrantio_operator_configurations[0]
            igrantio_operator_configuration.api_key = api_key
            igrantio_operator_configuration.org_id = org_id
            igrantio_operator_configuration.operator_endpoint = operator_endpoint

        await igrantio_operator_configuration.save(self.context, reason="Updated iGrant.io operator configuration")

        return igrantio_operator_configuration

    async def list_data_certificate_types_request(self, connection_id: str):

        request = ListDataCertificateTypesMessage()

        responder: BaseResponder = await self._context.inject(
            BaseResponder, required=False
        )
        if responder:
            await responder.send(request, connection_id=connection_id)

    async def get_list_data_certificate_types_response_message(self):
        storage = await self.context.inject(BaseStorage)
        found = await storage.search_records(
            type_filter=CRED_DEF_SENT_RECORD_TYPE,
            tag_query={}
        ).fetch_all()

        data_certificate_types = []

        if found:
            for record in found:
                temp_data_certificate_type = ListDataCertificateTypesResult(
                    schema_version=record.tags.get("schema_version"),
                    schema_name=record.tags.get("schema_name"),
                    epoch=record.tags.get("epoch"),
                    schema_id=record.tags.get("schema_id"),
                    cred_def_id=record.tags.get("cred_def_id"),
                    schema_issuer_did=record.tags.get("schema_issuer_did"),
                    issuer_did=record.tags.get("issuer_did"),
                    schema_attributes=json.loads(record.tags.get("schema_attributes"))
                )
                data_certificate_types.append(temp_data_certificate_type)

        response = ListDataCertificateTypesResponseMessage(
            data_certificate_types=data_certificate_types)

        return response

    async def send_organization_info_request(self, connection_id: str):

        request = OrganizationInfoMessage()

        responder: BaseResponder = await self._context.inject(
            BaseResponder, required=False
        )
        if responder:
            await responder.send(request, connection_id=connection_id)

    async def send_fetch_data_agreement_request_message(self, connection_id: str, exchange_template_id: str, exchange_mode: str):

        request = FetchDataAgreementMessage(exchange_template_id=exchange_template_id,
                                            exchange_mode=exchange_mode)

        responder: BaseResponder = await self._context.inject(
            BaseResponder, required=False
        )
        if responder:
            await responder.send(request, connection_id=connection_id)

    async def get_organization_info_message(self):

        igrantio_operator_mgr = IGrantIOOperatorManager(context=self.context)

        operator_configuration = {}
        operator_configuration = await igrantio_operator_mgr.fetch_operator_configuration()

        if not operator_configuration:
            operator_configuration = {
                "api_key": self.context.settings.get("igrantio_api_key"),
                "org_id": self.context.settings.get("igrantio_org_id"),
                "operator_endpoint": self.context.settings.get("igrantio_endpoint")
            }

        org_info_route = "/v1/organizations/{org_id}".format(
            org_id=operator_configuration["org_id"])

        headers = {'Authorization': 'ApiKey {}'.format(
            operator_configuration["api_key"])}

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(operator_configuration["operator_endpoint"] + org_info_route) as resp:
                if resp.status == 200:
                    resp_json = await resp.json()

                    if "Organization" in resp_json:
                        organization_details = resp_json["Organization"]

                        exclude_keys = [
                            "BillingInfo",
                            "Admins",
                            "HlcSupport",
                            "DataRetention",
                            "Enabled",
                            "Subs"
                        ]

                        for exclude_key in exclude_keys:
                            organization_details.pop(exclude_key, None)

                        response = OrganizationInfoResponseMessage(
                            org_id=organization_details["ID"],
                            name=organization_details["Name"],
                            cover_image_url=organization_details["CoverImageURL"] + "/web",
                            logo_image_url=organization_details["LogoImageURL"] + "/web",
                            location=organization_details["Location"],
                            org_type=organization_details["Type"]["Type"],
                            description=organization_details["Description"],
                            policy_url=organization_details["PolicyURL"],
                            eula_url=organization_details["EulaURL"],
                            privacy_dashboard=OrganizationPrivacyDashboard(
                                host_name=organization_details["PrivacyDashboard"]["HostName"],
                                version=organization_details["PrivacyDashboard"]["Version"],
                                status=organization_details["PrivacyDashboard"]["Status"],
                                delete=organization_details["PrivacyDashboard"]["Delete"]
                            )
                        )

                        return response
                else:
                    return None
        return None

    async def fetch_data_agreement(self, message: FetchDataAgreementMessage, receipt: MessageReceipt):

        igrantio_operator_mgr = IGrantIOOperatorManager(context=self.context)

        operator_configuration = {}
        operator_configuration = await igrantio_operator_mgr.fetch_operator_configuration()

        if not operator_configuration:
            operator_configuration = {
                "api_key": self.context.settings.get("igrantio_api_key"),
                "org_id": self.context.settings.get("igrantio_org_id"),
                "operator_endpoint": self.context.settings.get("igrantio_endpoint")
            }

        org_info_route = "/v1/organizations/{org_id}".format(
            org_id=operator_configuration["org_id"])

        purpose_by_ssiid_route = "/v1/organizations/{org_id}/purposes/ssi/{ssi_id}"

        headers = {'Authorization': 'ApiKey {}'.format(
            operator_configuration["api_key"])}

        # fetch auto_exchange_id based on qr_id
        #     then call iGrant.io api to fetch purpose details by auto_exchange_id (SSIID)

        ssi_id = ""
        purpose_details = {}

        if message.exchange_mode == "verify":
            storage = await self.context.inject(BaseStorage)
            qr_data_ex_records = await storage.search_records(
                type_filter=IGrantIOOperatorManager.ORG_AUTO_DX_QR_RECORD_TYPE,
                tag_query={
                    "qr_id": message.exchange_template_id
                }
            ).fetch_all()

            if qr_data_ex_records:
                ssi_id = qr_data_ex_records[0].tags.get("auto_data_ex_id")

        if message.exchange_mode == "issue":
            ssi_id = message.exchange_template_id

        # Call iGrant.io api to fetch purpose details by cred_def_id (SSIID)

        purpose_by_ssiid_route = purpose_by_ssiid_route.format(
            org_id=operator_configuration["org_id"], ssi_id=ssi_id)

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(operator_configuration["operator_endpoint"] + purpose_by_ssiid_route) as resp:
                if resp.status == 200:
                    resp_json = await resp.json()

                    lawful_basis_list = [
                        {
                            "ID": 0,
                            "Str": "Consent"
                        },
                        {
                            "ID": 1,
                            "Str": "Contract"
                        },
                        {
                            "ID": 2,
                            "Str": "Legal Obligation"
                        },
                        {
                            "ID": 3,
                            "Str": "Vital Interest"
                        },
                        {
                            "ID": 4,
                            "Str": "Public Task"
                        },
                        {
                            "ID": 5,
                            "Str": "Legitimate Interest"
                        }
                    ]

                    lawful_basis_of_processing = ""

                    for lawful_basis_item in lawful_basis_list:
                        if lawful_basis_item["ID"] == resp_json["Purpose"]["LawfulBasisOfProcessing"]:
                            lawful_basis_of_processing = lawful_basis_item["Str"]
                            break

                    purpose_details = {
                        "purpose": {
                            "id": resp_json["Purpose"]["ID"],
                            "name": resp_json["Purpose"]["Name"],
                            "lawful_basis_of_processing": lawful_basis_of_processing,
                            "description": resp_json["Purpose"]["Description"],
                            "lawful_usage": resp_json["Purpose"]["LawfulUsage"],
                            "policy_url": resp_json["Purpose"]["PolicyURL"],
                            "attribute_type": resp_json["Purpose"]["AttributeType"],
                            "jurisdiction": resp_json["Purpose"]["Jurisdiction"],
                            "disclosure": resp_json["Purpose"]["Disclosure"],
                            "industry_scope": resp_json["Purpose"]["IndustryScope"],
                            "data_retention": {
                                "retention_period": resp_json["Purpose"]["DataRetention"]["RetentionPeriod"],
                                "enabled": resp_json["Purpose"]["DataRetention"]["Enabled"]
                            },
                            "restriction": resp_json["Purpose"]["Restriction"],
                            "shared_3pp": resp_json["Purpose"]["Shared3PP"],
                            "ssi_id": resp_json["Purpose"]["SSIID"],
                        },
                        "templates": []
                    }

                    if resp_json["Templates"]:
                        for template in resp_json["Templates"]:
                            purpose_details["templates"].append(
                                {
                                    "id": template["ID"],
                                    "consent": template["Consent"]
                                }
                            )

        # fetch org details from iGrant.io

        org_details = {}

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(operator_configuration["operator_endpoint"] + org_info_route) as resp:
                if resp.status == 200:
                    resp_json = await resp.json()

                    if "Organization" in resp_json:
                        organization_details = resp_json["Organization"]

                        exclude_keys = [
                            "BillingInfo",
                            "Admins",
                            "HlcSupport",
                            "DataRetention",
                            "Enabled",
                            "Subs"
                        ]

                        for exclude_key in exclude_keys:
                            organization_details.pop(exclude_key, None)

                        org_details = {
                            "org_id": organization_details["ID"],
                            "name": organization_details["Name"],
                            "cover_image_url": organization_details["CoverImageURL"] + "/web",
                            "logo_image_url": organization_details["LogoImageURL"] + "/web",
                            "location": organization_details["Location"],
                            "org_type": organization_details["Type"]["Type"],
                            "description": organization_details["Description"],
                            "policy_url": organization_details["PolicyURL"],
                            "eula_url": organization_details["EulaURL"],
                            "privacy_dashboard": {
                                "host_name": organization_details["PrivacyDashboard"]["HostName"],
                                "version": organization_details["PrivacyDashboard"]["Version"],
                                "status": organization_details["PrivacyDashboard"]["Status"],
                                "delete": organization_details["PrivacyDashboard"]["Delete"]
                            }
                        }

        response = FetchDataAgreementResponseMessage(
            org_details=org_details, purpose_details=purpose_details)

        return response

    async def org_multiple_connections_record_status(self, message: OrgMultipleConnectionsMessage, receipt: MessageReceipt):
        connection_key = receipt.recipient_verkey
        try:
            # fetch connection record using invitation key
            connection = await ConnectionRecord.retrieve_by_invitation_key(
                self.context, connection_key)

            # Check if org_multiple_connections_doc exists
            storage = await self.context.inject(BaseStorage)
            org_multiple_connections_records = await storage.search_records(
                type_filter=IGrantIOOperatorManager.ORG_MULTIPLE_CONNECTIONS_RECORD_TYPE,
                tag_query={
                    "connection_id": connection.connection_id
                }
            ).fetch_all()

            if org_multiple_connections_records:
                # delete org_multiple_connections_doc record
                org_multiple_connections_record = org_multiple_connections_records[0]
                await storage.delete_record(org_multiple_connections_record)

            org_multiple_connections_record = None

            if (not message.theirdid) or (len(message.theirdid.strip()) == 0):
                # create org_multiple_connections_doc record with connection_status notavailable
                record_tags = {
                    "existing_connection_id": "",
                    "my_did": "",
                    "connection_status": "notavailable",
                    "connection_id": connection.connection_id
                }

                record = StorageRecord(
                    IGrantIOOperatorManager.ORG_MULTIPLE_CONNECTIONS_RECORD_TYPE,
                    connection.connection_id,
                    record_tags
                )
                await storage.add_record(record)
                return None

            # fetch the existing connection by did
            existing_connection = await ConnectionRecord.retrieve_by_did(
                self.context, their_did=None, my_did=message.theirdid)

            if not existing_connection:
                # create org_multiple_connections_doc record with connection_status notavailable
                record_tags = {
                    "existing_connection_id": "",
                    "my_did": "",
                    "connection_status": "notavailable",
                    "connection_id": connection.connection_id
                }

                record = StorageRecord(
                    IGrantIOOperatorManager.ORG_MULTIPLE_CONNECTIONS_RECORD_TYPE,
                    connection.connection_id,
                    record_tags
                )
                await storage.add_record(record)

                return None

            # create org_multiple_connections_doc record with connection_id, did, connection_status available
            record_tags = {
                "existing_connection_id": existing_connection.connection_id,
                "my_did": existing_connection.my_did,
                "connection_status": "available",
                "connection_id": connection.connection_id
            }

            record = StorageRecord(
                IGrantIOOperatorManager.ORG_MULTIPLE_CONNECTIONS_RECORD_TYPE,
                connection.connection_id,
                record_tags
            )
            await storage.add_record(record)

            # updating the new connection invitation status to inactive
            connection.state = ConnectionRecord.STATE_INACTIVE
            await connection.save(context=self.context)

        except StorageNotFoundError:
            raise ConnectionManagerError(
                "No invitation found for pairwise connection"
            )

    async def send_org_multiple_connections_info_message(self, connection_id: str, theirdid: str):

        request = OrgMultipleConnectionsMessage(theirdid=theirdid)

        responder: BaseResponder = await self._context.inject(
            BaseResponder, required=False
        )
        if responder:
            await responder.send(request, connection_id=connection_id)

    async def fetch_org_multiple_connections_record_by_connection_id(self, connection_id):
        storage = await self.context.inject(BaseStorage)
        org_multiple_connections_records = await storage.search_records(
            type_filter=IGrantIOOperatorManager.ORG_MULTIPLE_CONNECTIONS_RECORD_TYPE,
            tag_query={
                "connection_id": connection_id
            }
        ).fetch_all()

        record = {
            "existing_connection_id": "",
            "my_did": "",
            "connection_status": "notavailable",
            "connection_id": ""
        }

        if org_multiple_connections_records:
            record["existing_connection_id"] = org_multiple_connections_records[0].tags.get(
                "existing_connection_id")
            record["my_did"] = org_multiple_connections_records[0].tags.get("my_did")
            record["connection_status"] = org_multiple_connections_records[0].tags.get(
                "connection_status")
            record["connection_id"] = org_multiple_connections_records[0].tags.get(
                "connection_id")

        return record

    async def fetch_org_connection_invitation_json(self, connection_id):
        try:
            storage = await self.context.inject(BaseStorage)
            org_connection_invitation = await storage.search_records(
                type_filter=ConnectionRecord.RECORD_TYPE_INVITATION,
                tag_query={
                    "connection_id": connection_id
                }
            ).fetch_all()

            if org_connection_invitation:
                connection_invitation_json = json.loads(
                    org_connection_invitation[0].value)
                connection_invitation_url = connection_invitation_json["serviceEndpoint"] + "?c_i=" + base64.urlsafe_b64encode(
                    json.dumps(connection_invitation_json).encode("utf-8")).decode("utf-8")
                return connection_invitation_url

            return None
        except Exception:
            return None

    async def create_automated_data_exchange_record(self, presentation_request):
        storage = await self.context.inject(BaseStorage)
        record_tags = {
            "auto_data_ex_id": str(uuid.uuid4()),
            "created_time": str(int(datetime.datetime.utcnow().timestamp())),
        }

        record = StorageRecord(
            IGrantIOOperatorManager.ORG_AUTO_DATA_EXCHANGE_RECORD_TYPE,
            json.dumps(presentation_request),
            record_tags
        )
        await storage.add_record(record)

        result = {
            "auto_data_ex_id": record_tags.get("auto_data_ex_id"),
            "created_time": record_tags.get("created_time"),
            "presentation_request": presentation_request
        }

        return result

    async def list_automated_data_exchange_record(self):
        storage = await self.context.inject(BaseStorage)
        data_ex_records = await storage.search_records(
            type_filter=IGrantIOOperatorManager.ORG_AUTO_DATA_EXCHANGE_RECORD_TYPE,
            tag_query={}
        ).fetch_all()

        data_ex_result = []

        if data_ex_records:
            for data_ex_record in data_ex_records:
                temp_data_ex_record = {
                    "auto_data_ex_id": data_ex_record.tags.get("auto_data_ex_id"),
                    "presentation_request": json.loads(data_ex_record.value),
                }

                if data_ex_record.tags.get("created_time") is not None:
                    temp_data_ex_record["created_time"] = data_ex_record.tags.get("created_time")

                data_ex_result.append(temp_data_ex_record)
        
        # Sort data_ex_result of item by created_time if created_time exists and is not empty
        if data_ex_result:
            data_ex_result = sorted(data_ex_result, key=lambda k: ("created_time" in k ,k.get("created_time", None)))
            data_ex_result.reverse()

        return data_ex_result

    async def get_automated_data_exchange_record(self, auto_data_ex_id):
        storage = await self.context.inject(BaseStorage)
        data_ex_records = await storage.search_records(
            type_filter=IGrantIOOperatorManager.ORG_AUTO_DATA_EXCHANGE_RECORD_TYPE,
            tag_query={
                "auto_data_ex_id": auto_data_ex_id
            }
        ).fetch_all()

        data_ex_result = {}

        if data_ex_records:
            data_ex_result = {
                "auto_data_ex_id": data_ex_records[0].tags.get("auto_data_ex_id"),
                "presentation_request": json.loads(data_ex_records[0].value),
                "created_time": data_ex_records[0].tags.get("created_time")
            }

        return data_ex_result

    async def delete_automated_data_exchange_record(self, auto_data_ex_id):
        storage = await self.context.inject(BaseStorage)
        data_ex_records = await storage.search_records(
            type_filter=IGrantIOOperatorManager.ORG_AUTO_DATA_EXCHANGE_RECORD_TYPE,
            tag_query={
                "auto_data_ex_id": auto_data_ex_id
            }
        ).fetch_all()

        if data_ex_records:
            await storage.delete_record(data_ex_records[0])
            return True

        return False

    async def update_automated_data_exchange_record(self, auto_data_ex_id, presentation_request):
        storage = await self.context.inject(BaseStorage)
        data_ex_records = await storage.search_records(
            type_filter=IGrantIOOperatorManager.ORG_AUTO_DATA_EXCHANGE_RECORD_TYPE,
            tag_query={
                "auto_data_ex_id": auto_data_ex_id
            }
        ).fetch_all()

        if data_ex_records:
            await storage.update_record_value(data_ex_records[0], json.dumps(presentation_request))
            return {
                "auto_data_ex_id": auto_data_ex_id,
                "presentation_request": presentation_request
            }

        return None

    async def create_qr_automated_data_exchange_record(self, auto_data_ex_id):

        invitation_url = ""
        invitation_service_endpoint = ""

        # Fetch auto data exchange record

        storage = await self.context.inject(BaseStorage)
        data_ex_records = await storage.search_records(
            type_filter=IGrantIOOperatorManager.ORG_AUTO_DATA_EXCHANGE_RECORD_TYPE,
            tag_query={
                "auto_data_ex_id": auto_data_ex_id
            }
        ).fetch_all()

        if not data_ex_records:
            return None

        # Create QR auto data exchange record

        record_tags = {
            "auto_data_ex_id": data_ex_records[0].tags.get("auto_data_ex_id"),
            "qr_id": str(uuid.uuid4())
        }

        # Create connection invitation

        connection_mgr = ConnectionManager(self.context)
        try:
            (connection, invitation) = await connection_mgr.create_invitation(
                auto_accept=True, public=False, multi_use=True, alias=record_tags.get("qr_id")
            )

            invitation_url = invitation.to_url(
                self.context.settings.get("invite_base_url"))
            invitation_service_endpoint = invitation.serialize()["serviceEndpoint"]

        except (ConnectionManagerError, BaseModelError) as err:
            return None

        # Creating new nonce value for the presentation exchange
        new_nonce = await generate_pr_nonce()
        proof_request = json.loads(data_ex_records[0].value)
        proof_request["nonce"] = new_nonce

        print(proof_request)

        record_value = {
            "invitation_url": invitation_url,
            "proof_request": proof_request
        }

        dx_qr_url = invitation_service_endpoint + "?qr_p=" + base64.urlsafe_b64encode(
            json.dumps(record_value).encode("utf-8")).decode("utf-8")

        record_tags["connection_id"] = connection.connection_id
        record_tags["nonce"] = new_nonce

        record = StorageRecord(
            IGrantIOOperatorManager.ORG_AUTO_DX_QR_RECORD_TYPE,
            dx_qr_url,
            record_tags
        )
        await storage.add_record(record)

        result = {
            "auto_data_ex_id": record_tags.get("auto_data_ex_id"),
            "qr_id": record_tags.get("qr_id"),
            "qr_data": dx_qr_url,
            "connection_id": record_tags.get("connection_id"),
            "nonce": record_tags.get("nonce")
        }

        return result

    async def delete_qr_automated_data_exchange_record(self, qr_id):
        storage = await self.context.inject(BaseStorage)
        qr_data_ex_records = await storage.search_records(
            type_filter=IGrantIOOperatorManager.ORG_AUTO_DX_QR_RECORD_TYPE,
            tag_query={
                "qr_id": qr_id
            }
        ).fetch_all()

        if qr_data_ex_records:
            await storage.delete_record(qr_data_ex_records[0])
            return True

        return False

    async def get_qr_automated_data_exchange_record(self, qr_id):
        storage = await self.context.inject(BaseStorage)
        qr_data_ex_records = await storage.search_records(
            type_filter=IGrantIOOperatorManager.ORG_AUTO_DX_QR_RECORD_TYPE,
            tag_query={
                "qr_id": qr_id
            }
        ).fetch_all()

        data_ex_result = {}

        if qr_data_ex_records:
            data_ex_result = {
                "dataexchange_url": qr_data_ex_records[0].value
            }

        return data_ex_result

    async def list_qr_automated_data_exchange_record(self, auto_data_ex_id):
        storage = await self.context.inject(BaseStorage)
        qr_data_ex_records = await storage.search_records(
            type_filter=IGrantIOOperatorManager.ORG_AUTO_DX_QR_RECORD_TYPE,
            tag_query={
                "auto_data_ex_id": auto_data_ex_id
            }
        ).fetch_all()

        qr_data_ex_result = []

        if qr_data_ex_records:
            for qr_data_ex_record in qr_data_ex_records:
                temp_data_ex_record = {
                    "auto_data_ex_id": qr_data_ex_record.tags.get("auto_data_ex_id"),
                    "qr_id": qr_data_ex_record.tags.get("qr_id"),
                    "qr_data": qr_data_ex_record.value,
                    "connection_id": qr_data_ex_record.tags.get("connection_id"),
                    "nonce": qr_data_ex_record.tags.get("nonce")
                }
                qr_data_ex_result.append(temp_data_ex_record)

        return qr_data_ex_result
