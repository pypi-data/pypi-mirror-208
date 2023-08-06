"""Message type identifiers for Routing."""

from ...didcomm_prefix import DIDCommPrefix


# Message types
LIST_DATA_CERTIFICATE_TYPES = "igrantio-operator/1.0/list-data-certificate-types"
LIST_DATA_CERTIFICATE_TYPES_RESPONSE = "igrantio-operator/1.0/list-data-certificate-types-response"

PROBLEM_REPORT = "igrantio-operator/1.0/problem_report"

ORGANIZATION_INFO = "igrantio-operator/1.0/organization-info"
ORGANIZATION_INFO_RESPONSE = "igrantio-operator/1.0/organization-info-response"

ORG_MULTIPLE_CONNECTIONS = "igrantio-operator/1.0/org-multiple-connections"

FETCH_DATA_AGREEMENT = "igrantio-operator/1.0/fetch-data-agreement"
FETCH_DATA_AGREEMENT_RESPONSE = "igrantio-operator/1.0/fetch-data-agreement-response"

PROTOCOL_PACKAGE = "aries_cloudagent.protocols.igrantio_operator.v1_0"

MESSAGE_TYPES = DIDCommPrefix.qualify_all(
    {
        LIST_DATA_CERTIFICATE_TYPES: (
            f"{PROTOCOL_PACKAGE}.messages.list_data_certificate_types.ListDataCertificateTypesMessage"
        ),
        LIST_DATA_CERTIFICATE_TYPES_RESPONSE: (
            f"{PROTOCOL_PACKAGE}.messages.list_data_certificate_types_response.ListDataCertificateTypesResponseMessage"
        ),
        ORGANIZATION_INFO: (
            f"{PROTOCOL_PACKAGE}.messages.organization_info.OrganizationInfoMessage"
        ),
        ORGANIZATION_INFO_RESPONSE: (
            f"{PROTOCOL_PACKAGE}.messages.organization_info_response.OrganizationInfoResponseMessage"
        ),
        PROBLEM_REPORT: (
            f"{PROTOCOL_PACKAGE}.messages.problem_report.ProblemReport"
        ),
        ORG_MULTIPLE_CONNECTIONS: (
            f"{PROTOCOL_PACKAGE}.messages.org_multiple_connections.OrgMultipleConnectionsMessage"
        ),
        FETCH_DATA_AGREEMENT: (
            f"{PROTOCOL_PACKAGE}.messages.fetch_data_agreement.FetchDataAgreementMessage"
        ),
        FETCH_DATA_AGREEMENT_RESPONSE: (
            f"{PROTOCOL_PACKAGE}.messages.fetch_data_agreement_response.FetchDataAgreementResponseMessage"
        ),
    }
)
