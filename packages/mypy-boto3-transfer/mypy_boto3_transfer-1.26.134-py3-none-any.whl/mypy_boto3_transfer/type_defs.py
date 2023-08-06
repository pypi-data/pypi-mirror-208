"""
Type annotations for transfer service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_transfer/type_defs/)

Usage::

    ```python
    from mypy_boto3_transfer.type_defs import As2ConnectorConfigTypeDef

    data: As2ConnectorConfigTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Sequence, Union

from .literals import (
    AgreementStatusTypeType,
    CertificateStatusTypeType,
    CertificateTypeType,
    CertificateUsageTypeType,
    CompressionEnumType,
    CustomStepStatusType,
    DomainType,
    EncryptionAlgType,
    EndpointTypeType,
    ExecutionErrorTypeType,
    ExecutionStatusType,
    HomeDirectoryTypeType,
    IdentityProviderTypeType,
    MdnResponseType,
    MdnSigningAlgType,
    OverwriteExistingType,
    ProfileTypeType,
    ProtocolType,
    SetStatOptionType,
    SftpAuthenticationMethodsType,
    SigningAlgType,
    StateType,
    TlsSessionResumptionModeType,
    WorkflowStepTypeType,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "As2ConnectorConfigTypeDef",
    "HomeDirectoryMapEntryTypeDef",
    "PosixProfileTypeDef",
    "ResponseMetadataTypeDef",
    "TagTypeDef",
    "EndpointDetailsTypeDef",
    "IdentityProviderDetailsTypeDef",
    "ProtocolDetailsTypeDef",
    "CustomStepDetailsTypeDef",
    "DeleteAccessRequestRequestTypeDef",
    "DeleteAgreementRequestRequestTypeDef",
    "DeleteCertificateRequestRequestTypeDef",
    "DeleteConnectorRequestRequestTypeDef",
    "DeleteHostKeyRequestRequestTypeDef",
    "DeleteProfileRequestRequestTypeDef",
    "DeleteServerRequestRequestTypeDef",
    "DeleteSshPublicKeyRequestRequestTypeDef",
    "DeleteStepDetailsTypeDef",
    "DeleteUserRequestRequestTypeDef",
    "DeleteWorkflowRequestRequestTypeDef",
    "DescribeAccessRequestRequestTypeDef",
    "DescribeAgreementRequestRequestTypeDef",
    "DescribeCertificateRequestRequestTypeDef",
    "DescribeConnectorRequestRequestTypeDef",
    "DescribeExecutionRequestRequestTypeDef",
    "DescribeHostKeyRequestRequestTypeDef",
    "DescribeProfileRequestRequestTypeDef",
    "DescribeSecurityPolicyRequestRequestTypeDef",
    "DescribedSecurityPolicyTypeDef",
    "DescribeServerRequestRequestTypeDef",
    "WaiterConfigTypeDef",
    "DescribeUserRequestRequestTypeDef",
    "DescribeWorkflowRequestRequestTypeDef",
    "LoggingConfigurationTypeDef",
    "SshPublicKeyTypeDef",
    "EfsFileLocationTypeDef",
    "ExecutionErrorTypeDef",
    "S3FileLocationTypeDef",
    "ImportSshPublicKeyRequestRequestTypeDef",
    "S3InputFileLocationTypeDef",
    "PaginatorConfigTypeDef",
    "ListAccessesRequestRequestTypeDef",
    "ListedAccessTypeDef",
    "ListAgreementsRequestRequestTypeDef",
    "ListedAgreementTypeDef",
    "ListCertificatesRequestRequestTypeDef",
    "ListedCertificateTypeDef",
    "ListConnectorsRequestRequestTypeDef",
    "ListedConnectorTypeDef",
    "ListExecutionsRequestRequestTypeDef",
    "ListHostKeysRequestRequestTypeDef",
    "ListedHostKeyTypeDef",
    "ListProfilesRequestRequestTypeDef",
    "ListedProfileTypeDef",
    "ListSecurityPoliciesRequestRequestTypeDef",
    "ListServersRequestRequestTypeDef",
    "ListedServerTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListUsersRequestRequestTypeDef",
    "ListedUserTypeDef",
    "ListWorkflowsRequestRequestTypeDef",
    "ListedWorkflowTypeDef",
    "S3TagTypeDef",
    "SendWorkflowStepStateRequestRequestTypeDef",
    "UserDetailsTypeDef",
    "StartFileTransferRequestRequestTypeDef",
    "StartServerRequestRequestTypeDef",
    "StopServerRequestRequestTypeDef",
    "TestIdentityProviderRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateAgreementRequestRequestTypeDef",
    "UpdateCertificateRequestRequestTypeDef",
    "UpdateHostKeyRequestRequestTypeDef",
    "UpdateProfileRequestRequestTypeDef",
    "WorkflowDetailTypeDef",
    "UpdateConnectorRequestRequestTypeDef",
    "CreateAccessRequestRequestTypeDef",
    "DescribedAccessTypeDef",
    "UpdateAccessRequestRequestTypeDef",
    "UpdateUserRequestRequestTypeDef",
    "CreateAccessResponseTypeDef",
    "CreateAgreementResponseTypeDef",
    "CreateConnectorResponseTypeDef",
    "CreateProfileResponseTypeDef",
    "CreateServerResponseTypeDef",
    "CreateUserResponseTypeDef",
    "CreateWorkflowResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "ImportCertificateResponseTypeDef",
    "ImportHostKeyResponseTypeDef",
    "ImportSshPublicKeyResponseTypeDef",
    "ListSecurityPoliciesResponseTypeDef",
    "StartFileTransferResponseTypeDef",
    "TestIdentityProviderResponseTypeDef",
    "UpdateAccessResponseTypeDef",
    "UpdateAgreementResponseTypeDef",
    "UpdateCertificateResponseTypeDef",
    "UpdateConnectorResponseTypeDef",
    "UpdateHostKeyResponseTypeDef",
    "UpdateProfileResponseTypeDef",
    "UpdateServerResponseTypeDef",
    "UpdateUserResponseTypeDef",
    "CreateAgreementRequestRequestTypeDef",
    "CreateConnectorRequestRequestTypeDef",
    "CreateProfileRequestRequestTypeDef",
    "CreateUserRequestRequestTypeDef",
    "DescribedAgreementTypeDef",
    "DescribedCertificateTypeDef",
    "DescribedConnectorTypeDef",
    "DescribedHostKeyTypeDef",
    "DescribedProfileTypeDef",
    "ImportCertificateRequestRequestTypeDef",
    "ImportHostKeyRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "TagResourceRequestRequestTypeDef",
    "DescribeSecurityPolicyResponseTypeDef",
    "DescribeServerRequestServerOfflineWaitTypeDef",
    "DescribeServerRequestServerOnlineWaitTypeDef",
    "DescribedUserTypeDef",
    "ExecutionStepResultTypeDef",
    "FileLocationTypeDef",
    "InputFileLocationTypeDef",
    "ListAccessesRequestListAccessesPaginateTypeDef",
    "ListAgreementsRequestListAgreementsPaginateTypeDef",
    "ListCertificatesRequestListCertificatesPaginateTypeDef",
    "ListConnectorsRequestListConnectorsPaginateTypeDef",
    "ListExecutionsRequestListExecutionsPaginateTypeDef",
    "ListProfilesRequestListProfilesPaginateTypeDef",
    "ListSecurityPoliciesRequestListSecurityPoliciesPaginateTypeDef",
    "ListServersRequestListServersPaginateTypeDef",
    "ListTagsForResourceRequestListTagsForResourcePaginateTypeDef",
    "ListUsersRequestListUsersPaginateTypeDef",
    "ListWorkflowsRequestListWorkflowsPaginateTypeDef",
    "ListAccessesResponseTypeDef",
    "ListAgreementsResponseTypeDef",
    "ListCertificatesResponseTypeDef",
    "ListConnectorsResponseTypeDef",
    "ListHostKeysResponseTypeDef",
    "ListProfilesResponseTypeDef",
    "ListServersResponseTypeDef",
    "ListUsersResponseTypeDef",
    "ListWorkflowsResponseTypeDef",
    "TagStepDetailsTypeDef",
    "ServiceMetadataTypeDef",
    "WorkflowDetailsTypeDef",
    "DescribeAccessResponseTypeDef",
    "DescribeAgreementResponseTypeDef",
    "DescribeCertificateResponseTypeDef",
    "DescribeConnectorResponseTypeDef",
    "DescribeHostKeyResponseTypeDef",
    "DescribeProfileResponseTypeDef",
    "DescribeUserResponseTypeDef",
    "ExecutionResultsTypeDef",
    "CopyStepDetailsTypeDef",
    "DecryptStepDetailsTypeDef",
    "ListedExecutionTypeDef",
    "CreateServerRequestRequestTypeDef",
    "DescribedServerTypeDef",
    "UpdateServerRequestRequestTypeDef",
    "DescribedExecutionTypeDef",
    "WorkflowStepTypeDef",
    "ListExecutionsResponseTypeDef",
    "DescribeServerResponseTypeDef",
    "DescribeExecutionResponseTypeDef",
    "CreateWorkflowRequestRequestTypeDef",
    "DescribedWorkflowTypeDef",
    "DescribeWorkflowResponseTypeDef",
)

As2ConnectorConfigTypeDef = TypedDict(
    "As2ConnectorConfigTypeDef",
    {
        "LocalProfileId": str,
        "PartnerProfileId": str,
        "MessageSubject": str,
        "Compression": CompressionEnumType,
        "EncryptionAlgorithm": EncryptionAlgType,
        "SigningAlgorithm": SigningAlgType,
        "MdnSigningAlgorithm": MdnSigningAlgType,
        "MdnResponse": MdnResponseType,
    },
    total=False,
)

HomeDirectoryMapEntryTypeDef = TypedDict(
    "HomeDirectoryMapEntryTypeDef",
    {
        "Entry": str,
        "Target": str,
    },
)

_RequiredPosixProfileTypeDef = TypedDict(
    "_RequiredPosixProfileTypeDef",
    {
        "Uid": int,
        "Gid": int,
    },
)
_OptionalPosixProfileTypeDef = TypedDict(
    "_OptionalPosixProfileTypeDef",
    {
        "SecondaryGids": Sequence[int],
    },
    total=False,
)


class PosixProfileTypeDef(_RequiredPosixProfileTypeDef, _OptionalPosixProfileTypeDef):
    pass


ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)

EndpointDetailsTypeDef = TypedDict(
    "EndpointDetailsTypeDef",
    {
        "AddressAllocationIds": Sequence[str],
        "SubnetIds": Sequence[str],
        "VpcEndpointId": str,
        "VpcId": str,
        "SecurityGroupIds": Sequence[str],
    },
    total=False,
)

IdentityProviderDetailsTypeDef = TypedDict(
    "IdentityProviderDetailsTypeDef",
    {
        "Url": str,
        "InvocationRole": str,
        "DirectoryId": str,
        "Function": str,
        "SftpAuthenticationMethods": SftpAuthenticationMethodsType,
    },
    total=False,
)

ProtocolDetailsTypeDef = TypedDict(
    "ProtocolDetailsTypeDef",
    {
        "PassiveIp": str,
        "TlsSessionResumptionMode": TlsSessionResumptionModeType,
        "SetStatOption": SetStatOptionType,
        "As2Transports": Sequence[Literal["HTTP"]],
    },
    total=False,
)

CustomStepDetailsTypeDef = TypedDict(
    "CustomStepDetailsTypeDef",
    {
        "Name": str,
        "Target": str,
        "TimeoutSeconds": int,
        "SourceFileLocation": str,
    },
    total=False,
)

DeleteAccessRequestRequestTypeDef = TypedDict(
    "DeleteAccessRequestRequestTypeDef",
    {
        "ServerId": str,
        "ExternalId": str,
    },
)

DeleteAgreementRequestRequestTypeDef = TypedDict(
    "DeleteAgreementRequestRequestTypeDef",
    {
        "AgreementId": str,
        "ServerId": str,
    },
)

DeleteCertificateRequestRequestTypeDef = TypedDict(
    "DeleteCertificateRequestRequestTypeDef",
    {
        "CertificateId": str,
    },
)

DeleteConnectorRequestRequestTypeDef = TypedDict(
    "DeleteConnectorRequestRequestTypeDef",
    {
        "ConnectorId": str,
    },
)

DeleteHostKeyRequestRequestTypeDef = TypedDict(
    "DeleteHostKeyRequestRequestTypeDef",
    {
        "ServerId": str,
        "HostKeyId": str,
    },
)

DeleteProfileRequestRequestTypeDef = TypedDict(
    "DeleteProfileRequestRequestTypeDef",
    {
        "ProfileId": str,
    },
)

DeleteServerRequestRequestTypeDef = TypedDict(
    "DeleteServerRequestRequestTypeDef",
    {
        "ServerId": str,
    },
)

DeleteSshPublicKeyRequestRequestTypeDef = TypedDict(
    "DeleteSshPublicKeyRequestRequestTypeDef",
    {
        "ServerId": str,
        "SshPublicKeyId": str,
        "UserName": str,
    },
)

DeleteStepDetailsTypeDef = TypedDict(
    "DeleteStepDetailsTypeDef",
    {
        "Name": str,
        "SourceFileLocation": str,
    },
    total=False,
)

DeleteUserRequestRequestTypeDef = TypedDict(
    "DeleteUserRequestRequestTypeDef",
    {
        "ServerId": str,
        "UserName": str,
    },
)

DeleteWorkflowRequestRequestTypeDef = TypedDict(
    "DeleteWorkflowRequestRequestTypeDef",
    {
        "WorkflowId": str,
    },
)

DescribeAccessRequestRequestTypeDef = TypedDict(
    "DescribeAccessRequestRequestTypeDef",
    {
        "ServerId": str,
        "ExternalId": str,
    },
)

DescribeAgreementRequestRequestTypeDef = TypedDict(
    "DescribeAgreementRequestRequestTypeDef",
    {
        "AgreementId": str,
        "ServerId": str,
    },
)

DescribeCertificateRequestRequestTypeDef = TypedDict(
    "DescribeCertificateRequestRequestTypeDef",
    {
        "CertificateId": str,
    },
)

DescribeConnectorRequestRequestTypeDef = TypedDict(
    "DescribeConnectorRequestRequestTypeDef",
    {
        "ConnectorId": str,
    },
)

DescribeExecutionRequestRequestTypeDef = TypedDict(
    "DescribeExecutionRequestRequestTypeDef",
    {
        "ExecutionId": str,
        "WorkflowId": str,
    },
)

DescribeHostKeyRequestRequestTypeDef = TypedDict(
    "DescribeHostKeyRequestRequestTypeDef",
    {
        "ServerId": str,
        "HostKeyId": str,
    },
)

DescribeProfileRequestRequestTypeDef = TypedDict(
    "DescribeProfileRequestRequestTypeDef",
    {
        "ProfileId": str,
    },
)

DescribeSecurityPolicyRequestRequestTypeDef = TypedDict(
    "DescribeSecurityPolicyRequestRequestTypeDef",
    {
        "SecurityPolicyName": str,
    },
)

_RequiredDescribedSecurityPolicyTypeDef = TypedDict(
    "_RequiredDescribedSecurityPolicyTypeDef",
    {
        "SecurityPolicyName": str,
    },
)
_OptionalDescribedSecurityPolicyTypeDef = TypedDict(
    "_OptionalDescribedSecurityPolicyTypeDef",
    {
        "Fips": bool,
        "SshCiphers": List[str],
        "SshKexs": List[str],
        "SshMacs": List[str],
        "TlsCiphers": List[str],
    },
    total=False,
)


class DescribedSecurityPolicyTypeDef(
    _RequiredDescribedSecurityPolicyTypeDef, _OptionalDescribedSecurityPolicyTypeDef
):
    pass


DescribeServerRequestRequestTypeDef = TypedDict(
    "DescribeServerRequestRequestTypeDef",
    {
        "ServerId": str,
    },
)

WaiterConfigTypeDef = TypedDict(
    "WaiterConfigTypeDef",
    {
        "Delay": int,
        "MaxAttempts": int,
    },
    total=False,
)

DescribeUserRequestRequestTypeDef = TypedDict(
    "DescribeUserRequestRequestTypeDef",
    {
        "ServerId": str,
        "UserName": str,
    },
)

DescribeWorkflowRequestRequestTypeDef = TypedDict(
    "DescribeWorkflowRequestRequestTypeDef",
    {
        "WorkflowId": str,
    },
)

LoggingConfigurationTypeDef = TypedDict(
    "LoggingConfigurationTypeDef",
    {
        "LoggingRole": str,
        "LogGroupName": str,
    },
    total=False,
)

SshPublicKeyTypeDef = TypedDict(
    "SshPublicKeyTypeDef",
    {
        "DateImported": datetime,
        "SshPublicKeyBody": str,
        "SshPublicKeyId": str,
    },
)

EfsFileLocationTypeDef = TypedDict(
    "EfsFileLocationTypeDef",
    {
        "FileSystemId": str,
        "Path": str,
    },
    total=False,
)

ExecutionErrorTypeDef = TypedDict(
    "ExecutionErrorTypeDef",
    {
        "Type": ExecutionErrorTypeType,
        "Message": str,
    },
)

S3FileLocationTypeDef = TypedDict(
    "S3FileLocationTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "VersionId": str,
        "Etag": str,
    },
    total=False,
)

ImportSshPublicKeyRequestRequestTypeDef = TypedDict(
    "ImportSshPublicKeyRequestRequestTypeDef",
    {
        "ServerId": str,
        "SshPublicKeyBody": str,
        "UserName": str,
    },
)

S3InputFileLocationTypeDef = TypedDict(
    "S3InputFileLocationTypeDef",
    {
        "Bucket": str,
        "Key": str,
    },
    total=False,
)

PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": int,
        "PageSize": int,
        "StartingToken": str,
    },
    total=False,
)

_RequiredListAccessesRequestRequestTypeDef = TypedDict(
    "_RequiredListAccessesRequestRequestTypeDef",
    {
        "ServerId": str,
    },
)
_OptionalListAccessesRequestRequestTypeDef = TypedDict(
    "_OptionalListAccessesRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListAccessesRequestRequestTypeDef(
    _RequiredListAccessesRequestRequestTypeDef, _OptionalListAccessesRequestRequestTypeDef
):
    pass


ListedAccessTypeDef = TypedDict(
    "ListedAccessTypeDef",
    {
        "HomeDirectory": str,
        "HomeDirectoryType": HomeDirectoryTypeType,
        "Role": str,
        "ExternalId": str,
    },
    total=False,
)

_RequiredListAgreementsRequestRequestTypeDef = TypedDict(
    "_RequiredListAgreementsRequestRequestTypeDef",
    {
        "ServerId": str,
    },
)
_OptionalListAgreementsRequestRequestTypeDef = TypedDict(
    "_OptionalListAgreementsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListAgreementsRequestRequestTypeDef(
    _RequiredListAgreementsRequestRequestTypeDef, _OptionalListAgreementsRequestRequestTypeDef
):
    pass


ListedAgreementTypeDef = TypedDict(
    "ListedAgreementTypeDef",
    {
        "Arn": str,
        "AgreementId": str,
        "Description": str,
        "Status": AgreementStatusTypeType,
        "ServerId": str,
        "LocalProfileId": str,
        "PartnerProfileId": str,
    },
    total=False,
)

ListCertificatesRequestRequestTypeDef = TypedDict(
    "ListCertificatesRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListedCertificateTypeDef = TypedDict(
    "ListedCertificateTypeDef",
    {
        "Arn": str,
        "CertificateId": str,
        "Usage": CertificateUsageTypeType,
        "Status": CertificateStatusTypeType,
        "ActiveDate": datetime,
        "InactiveDate": datetime,
        "Type": CertificateTypeType,
        "Description": str,
    },
    total=False,
)

ListConnectorsRequestRequestTypeDef = TypedDict(
    "ListConnectorsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListedConnectorTypeDef = TypedDict(
    "ListedConnectorTypeDef",
    {
        "Arn": str,
        "ConnectorId": str,
        "Url": str,
    },
    total=False,
)

_RequiredListExecutionsRequestRequestTypeDef = TypedDict(
    "_RequiredListExecutionsRequestRequestTypeDef",
    {
        "WorkflowId": str,
    },
)
_OptionalListExecutionsRequestRequestTypeDef = TypedDict(
    "_OptionalListExecutionsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListExecutionsRequestRequestTypeDef(
    _RequiredListExecutionsRequestRequestTypeDef, _OptionalListExecutionsRequestRequestTypeDef
):
    pass


_RequiredListHostKeysRequestRequestTypeDef = TypedDict(
    "_RequiredListHostKeysRequestRequestTypeDef",
    {
        "ServerId": str,
    },
)
_OptionalListHostKeysRequestRequestTypeDef = TypedDict(
    "_OptionalListHostKeysRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListHostKeysRequestRequestTypeDef(
    _RequiredListHostKeysRequestRequestTypeDef, _OptionalListHostKeysRequestRequestTypeDef
):
    pass


_RequiredListedHostKeyTypeDef = TypedDict(
    "_RequiredListedHostKeyTypeDef",
    {
        "Arn": str,
    },
)
_OptionalListedHostKeyTypeDef = TypedDict(
    "_OptionalListedHostKeyTypeDef",
    {
        "HostKeyId": str,
        "Fingerprint": str,
        "Description": str,
        "Type": str,
        "DateImported": datetime,
    },
    total=False,
)


class ListedHostKeyTypeDef(_RequiredListedHostKeyTypeDef, _OptionalListedHostKeyTypeDef):
    pass


ListProfilesRequestRequestTypeDef = TypedDict(
    "ListProfilesRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
        "ProfileType": ProfileTypeType,
    },
    total=False,
)

ListedProfileTypeDef = TypedDict(
    "ListedProfileTypeDef",
    {
        "Arn": str,
        "ProfileId": str,
        "As2Id": str,
        "ProfileType": ProfileTypeType,
    },
    total=False,
)

ListSecurityPoliciesRequestRequestTypeDef = TypedDict(
    "ListSecurityPoliciesRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListServersRequestRequestTypeDef = TypedDict(
    "ListServersRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

_RequiredListedServerTypeDef = TypedDict(
    "_RequiredListedServerTypeDef",
    {
        "Arn": str,
    },
)
_OptionalListedServerTypeDef = TypedDict(
    "_OptionalListedServerTypeDef",
    {
        "Domain": DomainType,
        "IdentityProviderType": IdentityProviderTypeType,
        "EndpointType": EndpointTypeType,
        "LoggingRole": str,
        "ServerId": str,
        "State": StateType,
        "UserCount": int,
    },
    total=False,
)


class ListedServerTypeDef(_RequiredListedServerTypeDef, _OptionalListedServerTypeDef):
    pass


_RequiredListTagsForResourceRequestRequestTypeDef = TypedDict(
    "_RequiredListTagsForResourceRequestRequestTypeDef",
    {
        "Arn": str,
    },
)
_OptionalListTagsForResourceRequestRequestTypeDef = TypedDict(
    "_OptionalListTagsForResourceRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListTagsForResourceRequestRequestTypeDef(
    _RequiredListTagsForResourceRequestRequestTypeDef,
    _OptionalListTagsForResourceRequestRequestTypeDef,
):
    pass


_RequiredListUsersRequestRequestTypeDef = TypedDict(
    "_RequiredListUsersRequestRequestTypeDef",
    {
        "ServerId": str,
    },
)
_OptionalListUsersRequestRequestTypeDef = TypedDict(
    "_OptionalListUsersRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListUsersRequestRequestTypeDef(
    _RequiredListUsersRequestRequestTypeDef, _OptionalListUsersRequestRequestTypeDef
):
    pass


_RequiredListedUserTypeDef = TypedDict(
    "_RequiredListedUserTypeDef",
    {
        "Arn": str,
    },
)
_OptionalListedUserTypeDef = TypedDict(
    "_OptionalListedUserTypeDef",
    {
        "HomeDirectory": str,
        "HomeDirectoryType": HomeDirectoryTypeType,
        "Role": str,
        "SshPublicKeyCount": int,
        "UserName": str,
    },
    total=False,
)


class ListedUserTypeDef(_RequiredListedUserTypeDef, _OptionalListedUserTypeDef):
    pass


ListWorkflowsRequestRequestTypeDef = TypedDict(
    "ListWorkflowsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListedWorkflowTypeDef = TypedDict(
    "ListedWorkflowTypeDef",
    {
        "WorkflowId": str,
        "Description": str,
        "Arn": str,
    },
    total=False,
)

S3TagTypeDef = TypedDict(
    "S3TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)

SendWorkflowStepStateRequestRequestTypeDef = TypedDict(
    "SendWorkflowStepStateRequestRequestTypeDef",
    {
        "WorkflowId": str,
        "ExecutionId": str,
        "Token": str,
        "Status": CustomStepStatusType,
    },
)

_RequiredUserDetailsTypeDef = TypedDict(
    "_RequiredUserDetailsTypeDef",
    {
        "UserName": str,
        "ServerId": str,
    },
)
_OptionalUserDetailsTypeDef = TypedDict(
    "_OptionalUserDetailsTypeDef",
    {
        "SessionId": str,
    },
    total=False,
)


class UserDetailsTypeDef(_RequiredUserDetailsTypeDef, _OptionalUserDetailsTypeDef):
    pass


StartFileTransferRequestRequestTypeDef = TypedDict(
    "StartFileTransferRequestRequestTypeDef",
    {
        "ConnectorId": str,
        "SendFilePaths": Sequence[str],
    },
)

StartServerRequestRequestTypeDef = TypedDict(
    "StartServerRequestRequestTypeDef",
    {
        "ServerId": str,
    },
)

StopServerRequestRequestTypeDef = TypedDict(
    "StopServerRequestRequestTypeDef",
    {
        "ServerId": str,
    },
)

_RequiredTestIdentityProviderRequestRequestTypeDef = TypedDict(
    "_RequiredTestIdentityProviderRequestRequestTypeDef",
    {
        "ServerId": str,
        "UserName": str,
    },
)
_OptionalTestIdentityProviderRequestRequestTypeDef = TypedDict(
    "_OptionalTestIdentityProviderRequestRequestTypeDef",
    {
        "ServerProtocol": ProtocolType,
        "SourceIp": str,
        "UserPassword": str,
    },
    total=False,
)


class TestIdentityProviderRequestRequestTypeDef(
    _RequiredTestIdentityProviderRequestRequestTypeDef,
    _OptionalTestIdentityProviderRequestRequestTypeDef,
):
    pass


UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "Arn": str,
        "TagKeys": Sequence[str],
    },
)

_RequiredUpdateAgreementRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateAgreementRequestRequestTypeDef",
    {
        "AgreementId": str,
        "ServerId": str,
    },
)
_OptionalUpdateAgreementRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateAgreementRequestRequestTypeDef",
    {
        "Description": str,
        "Status": AgreementStatusTypeType,
        "LocalProfileId": str,
        "PartnerProfileId": str,
        "BaseDirectory": str,
        "AccessRole": str,
    },
    total=False,
)


class UpdateAgreementRequestRequestTypeDef(
    _RequiredUpdateAgreementRequestRequestTypeDef, _OptionalUpdateAgreementRequestRequestTypeDef
):
    pass


_RequiredUpdateCertificateRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateCertificateRequestRequestTypeDef",
    {
        "CertificateId": str,
    },
)
_OptionalUpdateCertificateRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateCertificateRequestRequestTypeDef",
    {
        "ActiveDate": Union[datetime, str],
        "InactiveDate": Union[datetime, str],
        "Description": str,
    },
    total=False,
)


class UpdateCertificateRequestRequestTypeDef(
    _RequiredUpdateCertificateRequestRequestTypeDef, _OptionalUpdateCertificateRequestRequestTypeDef
):
    pass


UpdateHostKeyRequestRequestTypeDef = TypedDict(
    "UpdateHostKeyRequestRequestTypeDef",
    {
        "ServerId": str,
        "HostKeyId": str,
        "Description": str,
    },
)

_RequiredUpdateProfileRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateProfileRequestRequestTypeDef",
    {
        "ProfileId": str,
    },
)
_OptionalUpdateProfileRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateProfileRequestRequestTypeDef",
    {
        "CertificateIds": Sequence[str],
    },
    total=False,
)


class UpdateProfileRequestRequestTypeDef(
    _RequiredUpdateProfileRequestRequestTypeDef, _OptionalUpdateProfileRequestRequestTypeDef
):
    pass


WorkflowDetailTypeDef = TypedDict(
    "WorkflowDetailTypeDef",
    {
        "WorkflowId": str,
        "ExecutionRole": str,
    },
)

_RequiredUpdateConnectorRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateConnectorRequestRequestTypeDef",
    {
        "ConnectorId": str,
    },
)
_OptionalUpdateConnectorRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateConnectorRequestRequestTypeDef",
    {
        "Url": str,
        "As2Config": As2ConnectorConfigTypeDef,
        "AccessRole": str,
        "LoggingRole": str,
    },
    total=False,
)


class UpdateConnectorRequestRequestTypeDef(
    _RequiredUpdateConnectorRequestRequestTypeDef, _OptionalUpdateConnectorRequestRequestTypeDef
):
    pass


_RequiredCreateAccessRequestRequestTypeDef = TypedDict(
    "_RequiredCreateAccessRequestRequestTypeDef",
    {
        "Role": str,
        "ServerId": str,
        "ExternalId": str,
    },
)
_OptionalCreateAccessRequestRequestTypeDef = TypedDict(
    "_OptionalCreateAccessRequestRequestTypeDef",
    {
        "HomeDirectory": str,
        "HomeDirectoryType": HomeDirectoryTypeType,
        "HomeDirectoryMappings": Sequence[HomeDirectoryMapEntryTypeDef],
        "Policy": str,
        "PosixProfile": PosixProfileTypeDef,
    },
    total=False,
)


class CreateAccessRequestRequestTypeDef(
    _RequiredCreateAccessRequestRequestTypeDef, _OptionalCreateAccessRequestRequestTypeDef
):
    pass


DescribedAccessTypeDef = TypedDict(
    "DescribedAccessTypeDef",
    {
        "HomeDirectory": str,
        "HomeDirectoryMappings": List[HomeDirectoryMapEntryTypeDef],
        "HomeDirectoryType": HomeDirectoryTypeType,
        "Policy": str,
        "PosixProfile": PosixProfileTypeDef,
        "Role": str,
        "ExternalId": str,
    },
    total=False,
)

_RequiredUpdateAccessRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateAccessRequestRequestTypeDef",
    {
        "ServerId": str,
        "ExternalId": str,
    },
)
_OptionalUpdateAccessRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateAccessRequestRequestTypeDef",
    {
        "HomeDirectory": str,
        "HomeDirectoryType": HomeDirectoryTypeType,
        "HomeDirectoryMappings": Sequence[HomeDirectoryMapEntryTypeDef],
        "Policy": str,
        "PosixProfile": PosixProfileTypeDef,
        "Role": str,
    },
    total=False,
)


class UpdateAccessRequestRequestTypeDef(
    _RequiredUpdateAccessRequestRequestTypeDef, _OptionalUpdateAccessRequestRequestTypeDef
):
    pass


_RequiredUpdateUserRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateUserRequestRequestTypeDef",
    {
        "ServerId": str,
        "UserName": str,
    },
)
_OptionalUpdateUserRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateUserRequestRequestTypeDef",
    {
        "HomeDirectory": str,
        "HomeDirectoryType": HomeDirectoryTypeType,
        "HomeDirectoryMappings": Sequence[HomeDirectoryMapEntryTypeDef],
        "Policy": str,
        "PosixProfile": PosixProfileTypeDef,
        "Role": str,
    },
    total=False,
)


class UpdateUserRequestRequestTypeDef(
    _RequiredUpdateUserRequestRequestTypeDef, _OptionalUpdateUserRequestRequestTypeDef
):
    pass


CreateAccessResponseTypeDef = TypedDict(
    "CreateAccessResponseTypeDef",
    {
        "ServerId": str,
        "ExternalId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateAgreementResponseTypeDef = TypedDict(
    "CreateAgreementResponseTypeDef",
    {
        "AgreementId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateConnectorResponseTypeDef = TypedDict(
    "CreateConnectorResponseTypeDef",
    {
        "ConnectorId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateProfileResponseTypeDef = TypedDict(
    "CreateProfileResponseTypeDef",
    {
        "ProfileId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateServerResponseTypeDef = TypedDict(
    "CreateServerResponseTypeDef",
    {
        "ServerId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateUserResponseTypeDef = TypedDict(
    "CreateUserResponseTypeDef",
    {
        "ServerId": str,
        "UserName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateWorkflowResponseTypeDef = TypedDict(
    "CreateWorkflowResponseTypeDef",
    {
        "WorkflowId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportCertificateResponseTypeDef = TypedDict(
    "ImportCertificateResponseTypeDef",
    {
        "CertificateId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportHostKeyResponseTypeDef = TypedDict(
    "ImportHostKeyResponseTypeDef",
    {
        "ServerId": str,
        "HostKeyId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportSshPublicKeyResponseTypeDef = TypedDict(
    "ImportSshPublicKeyResponseTypeDef",
    {
        "ServerId": str,
        "SshPublicKeyId": str,
        "UserName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListSecurityPoliciesResponseTypeDef = TypedDict(
    "ListSecurityPoliciesResponseTypeDef",
    {
        "NextToken": str,
        "SecurityPolicyNames": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartFileTransferResponseTypeDef = TypedDict(
    "StartFileTransferResponseTypeDef",
    {
        "TransferId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TestIdentityProviderResponseTypeDef = TypedDict(
    "TestIdentityProviderResponseTypeDef",
    {
        "Response": str,
        "StatusCode": int,
        "Message": str,
        "Url": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateAccessResponseTypeDef = TypedDict(
    "UpdateAccessResponseTypeDef",
    {
        "ServerId": str,
        "ExternalId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateAgreementResponseTypeDef = TypedDict(
    "UpdateAgreementResponseTypeDef",
    {
        "AgreementId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateCertificateResponseTypeDef = TypedDict(
    "UpdateCertificateResponseTypeDef",
    {
        "CertificateId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateConnectorResponseTypeDef = TypedDict(
    "UpdateConnectorResponseTypeDef",
    {
        "ConnectorId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateHostKeyResponseTypeDef = TypedDict(
    "UpdateHostKeyResponseTypeDef",
    {
        "ServerId": str,
        "HostKeyId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateProfileResponseTypeDef = TypedDict(
    "UpdateProfileResponseTypeDef",
    {
        "ProfileId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateServerResponseTypeDef = TypedDict(
    "UpdateServerResponseTypeDef",
    {
        "ServerId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateUserResponseTypeDef = TypedDict(
    "UpdateUserResponseTypeDef",
    {
        "ServerId": str,
        "UserName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCreateAgreementRequestRequestTypeDef = TypedDict(
    "_RequiredCreateAgreementRequestRequestTypeDef",
    {
        "ServerId": str,
        "LocalProfileId": str,
        "PartnerProfileId": str,
        "BaseDirectory": str,
        "AccessRole": str,
    },
)
_OptionalCreateAgreementRequestRequestTypeDef = TypedDict(
    "_OptionalCreateAgreementRequestRequestTypeDef",
    {
        "Description": str,
        "Status": AgreementStatusTypeType,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateAgreementRequestRequestTypeDef(
    _RequiredCreateAgreementRequestRequestTypeDef, _OptionalCreateAgreementRequestRequestTypeDef
):
    pass


_RequiredCreateConnectorRequestRequestTypeDef = TypedDict(
    "_RequiredCreateConnectorRequestRequestTypeDef",
    {
        "Url": str,
        "As2Config": As2ConnectorConfigTypeDef,
        "AccessRole": str,
    },
)
_OptionalCreateConnectorRequestRequestTypeDef = TypedDict(
    "_OptionalCreateConnectorRequestRequestTypeDef",
    {
        "LoggingRole": str,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateConnectorRequestRequestTypeDef(
    _RequiredCreateConnectorRequestRequestTypeDef, _OptionalCreateConnectorRequestRequestTypeDef
):
    pass


_RequiredCreateProfileRequestRequestTypeDef = TypedDict(
    "_RequiredCreateProfileRequestRequestTypeDef",
    {
        "As2Id": str,
        "ProfileType": ProfileTypeType,
    },
)
_OptionalCreateProfileRequestRequestTypeDef = TypedDict(
    "_OptionalCreateProfileRequestRequestTypeDef",
    {
        "CertificateIds": Sequence[str],
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateProfileRequestRequestTypeDef(
    _RequiredCreateProfileRequestRequestTypeDef, _OptionalCreateProfileRequestRequestTypeDef
):
    pass


_RequiredCreateUserRequestRequestTypeDef = TypedDict(
    "_RequiredCreateUserRequestRequestTypeDef",
    {
        "Role": str,
        "ServerId": str,
        "UserName": str,
    },
)
_OptionalCreateUserRequestRequestTypeDef = TypedDict(
    "_OptionalCreateUserRequestRequestTypeDef",
    {
        "HomeDirectory": str,
        "HomeDirectoryType": HomeDirectoryTypeType,
        "HomeDirectoryMappings": Sequence[HomeDirectoryMapEntryTypeDef],
        "Policy": str,
        "PosixProfile": PosixProfileTypeDef,
        "SshPublicKeyBody": str,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateUserRequestRequestTypeDef(
    _RequiredCreateUserRequestRequestTypeDef, _OptionalCreateUserRequestRequestTypeDef
):
    pass


_RequiredDescribedAgreementTypeDef = TypedDict(
    "_RequiredDescribedAgreementTypeDef",
    {
        "Arn": str,
    },
)
_OptionalDescribedAgreementTypeDef = TypedDict(
    "_OptionalDescribedAgreementTypeDef",
    {
        "AgreementId": str,
        "Description": str,
        "Status": AgreementStatusTypeType,
        "ServerId": str,
        "LocalProfileId": str,
        "PartnerProfileId": str,
        "BaseDirectory": str,
        "AccessRole": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)


class DescribedAgreementTypeDef(
    _RequiredDescribedAgreementTypeDef, _OptionalDescribedAgreementTypeDef
):
    pass


_RequiredDescribedCertificateTypeDef = TypedDict(
    "_RequiredDescribedCertificateTypeDef",
    {
        "Arn": str,
    },
)
_OptionalDescribedCertificateTypeDef = TypedDict(
    "_OptionalDescribedCertificateTypeDef",
    {
        "CertificateId": str,
        "Usage": CertificateUsageTypeType,
        "Status": CertificateStatusTypeType,
        "Certificate": str,
        "CertificateChain": str,
        "ActiveDate": datetime,
        "InactiveDate": datetime,
        "Serial": str,
        "NotBeforeDate": datetime,
        "NotAfterDate": datetime,
        "Type": CertificateTypeType,
        "Description": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)


class DescribedCertificateTypeDef(
    _RequiredDescribedCertificateTypeDef, _OptionalDescribedCertificateTypeDef
):
    pass


_RequiredDescribedConnectorTypeDef = TypedDict(
    "_RequiredDescribedConnectorTypeDef",
    {
        "Arn": str,
    },
)
_OptionalDescribedConnectorTypeDef = TypedDict(
    "_OptionalDescribedConnectorTypeDef",
    {
        "ConnectorId": str,
        "Url": str,
        "As2Config": As2ConnectorConfigTypeDef,
        "AccessRole": str,
        "LoggingRole": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)


class DescribedConnectorTypeDef(
    _RequiredDescribedConnectorTypeDef, _OptionalDescribedConnectorTypeDef
):
    pass


_RequiredDescribedHostKeyTypeDef = TypedDict(
    "_RequiredDescribedHostKeyTypeDef",
    {
        "Arn": str,
    },
)
_OptionalDescribedHostKeyTypeDef = TypedDict(
    "_OptionalDescribedHostKeyTypeDef",
    {
        "HostKeyId": str,
        "HostKeyFingerprint": str,
        "Description": str,
        "Type": str,
        "DateImported": datetime,
        "Tags": List[TagTypeDef],
    },
    total=False,
)


class DescribedHostKeyTypeDef(_RequiredDescribedHostKeyTypeDef, _OptionalDescribedHostKeyTypeDef):
    pass


_RequiredDescribedProfileTypeDef = TypedDict(
    "_RequiredDescribedProfileTypeDef",
    {
        "Arn": str,
    },
)
_OptionalDescribedProfileTypeDef = TypedDict(
    "_OptionalDescribedProfileTypeDef",
    {
        "ProfileId": str,
        "ProfileType": ProfileTypeType,
        "As2Id": str,
        "CertificateIds": List[str],
        "Tags": List[TagTypeDef],
    },
    total=False,
)


class DescribedProfileTypeDef(_RequiredDescribedProfileTypeDef, _OptionalDescribedProfileTypeDef):
    pass


_RequiredImportCertificateRequestRequestTypeDef = TypedDict(
    "_RequiredImportCertificateRequestRequestTypeDef",
    {
        "Usage": CertificateUsageTypeType,
        "Certificate": str,
    },
)
_OptionalImportCertificateRequestRequestTypeDef = TypedDict(
    "_OptionalImportCertificateRequestRequestTypeDef",
    {
        "CertificateChain": str,
        "PrivateKey": str,
        "ActiveDate": Union[datetime, str],
        "InactiveDate": Union[datetime, str],
        "Description": str,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class ImportCertificateRequestRequestTypeDef(
    _RequiredImportCertificateRequestRequestTypeDef, _OptionalImportCertificateRequestRequestTypeDef
):
    pass


_RequiredImportHostKeyRequestRequestTypeDef = TypedDict(
    "_RequiredImportHostKeyRequestRequestTypeDef",
    {
        "ServerId": str,
        "HostKeyBody": str,
    },
)
_OptionalImportHostKeyRequestRequestTypeDef = TypedDict(
    "_OptionalImportHostKeyRequestRequestTypeDef",
    {
        "Description": str,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class ImportHostKeyRequestRequestTypeDef(
    _RequiredImportHostKeyRequestRequestTypeDef, _OptionalImportHostKeyRequestRequestTypeDef
):
    pass


ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "Arn": str,
        "NextToken": str,
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "Arn": str,
        "Tags": Sequence[TagTypeDef],
    },
)

DescribeSecurityPolicyResponseTypeDef = TypedDict(
    "DescribeSecurityPolicyResponseTypeDef",
    {
        "SecurityPolicy": DescribedSecurityPolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredDescribeServerRequestServerOfflineWaitTypeDef = TypedDict(
    "_RequiredDescribeServerRequestServerOfflineWaitTypeDef",
    {
        "ServerId": str,
    },
)
_OptionalDescribeServerRequestServerOfflineWaitTypeDef = TypedDict(
    "_OptionalDescribeServerRequestServerOfflineWaitTypeDef",
    {
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)


class DescribeServerRequestServerOfflineWaitTypeDef(
    _RequiredDescribeServerRequestServerOfflineWaitTypeDef,
    _OptionalDescribeServerRequestServerOfflineWaitTypeDef,
):
    pass


_RequiredDescribeServerRequestServerOnlineWaitTypeDef = TypedDict(
    "_RequiredDescribeServerRequestServerOnlineWaitTypeDef",
    {
        "ServerId": str,
    },
)
_OptionalDescribeServerRequestServerOnlineWaitTypeDef = TypedDict(
    "_OptionalDescribeServerRequestServerOnlineWaitTypeDef",
    {
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)


class DescribeServerRequestServerOnlineWaitTypeDef(
    _RequiredDescribeServerRequestServerOnlineWaitTypeDef,
    _OptionalDescribeServerRequestServerOnlineWaitTypeDef,
):
    pass


_RequiredDescribedUserTypeDef = TypedDict(
    "_RequiredDescribedUserTypeDef",
    {
        "Arn": str,
    },
)
_OptionalDescribedUserTypeDef = TypedDict(
    "_OptionalDescribedUserTypeDef",
    {
        "HomeDirectory": str,
        "HomeDirectoryMappings": List[HomeDirectoryMapEntryTypeDef],
        "HomeDirectoryType": HomeDirectoryTypeType,
        "Policy": str,
        "PosixProfile": PosixProfileTypeDef,
        "Role": str,
        "SshPublicKeys": List[SshPublicKeyTypeDef],
        "Tags": List[TagTypeDef],
        "UserName": str,
    },
    total=False,
)


class DescribedUserTypeDef(_RequiredDescribedUserTypeDef, _OptionalDescribedUserTypeDef):
    pass


ExecutionStepResultTypeDef = TypedDict(
    "ExecutionStepResultTypeDef",
    {
        "StepType": WorkflowStepTypeType,
        "Outputs": str,
        "Error": ExecutionErrorTypeDef,
    },
    total=False,
)

FileLocationTypeDef = TypedDict(
    "FileLocationTypeDef",
    {
        "S3FileLocation": S3FileLocationTypeDef,
        "EfsFileLocation": EfsFileLocationTypeDef,
    },
    total=False,
)

InputFileLocationTypeDef = TypedDict(
    "InputFileLocationTypeDef",
    {
        "S3FileLocation": S3InputFileLocationTypeDef,
        "EfsFileLocation": EfsFileLocationTypeDef,
    },
    total=False,
)

_RequiredListAccessesRequestListAccessesPaginateTypeDef = TypedDict(
    "_RequiredListAccessesRequestListAccessesPaginateTypeDef",
    {
        "ServerId": str,
    },
)
_OptionalListAccessesRequestListAccessesPaginateTypeDef = TypedDict(
    "_OptionalListAccessesRequestListAccessesPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class ListAccessesRequestListAccessesPaginateTypeDef(
    _RequiredListAccessesRequestListAccessesPaginateTypeDef,
    _OptionalListAccessesRequestListAccessesPaginateTypeDef,
):
    pass


_RequiredListAgreementsRequestListAgreementsPaginateTypeDef = TypedDict(
    "_RequiredListAgreementsRequestListAgreementsPaginateTypeDef",
    {
        "ServerId": str,
    },
)
_OptionalListAgreementsRequestListAgreementsPaginateTypeDef = TypedDict(
    "_OptionalListAgreementsRequestListAgreementsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class ListAgreementsRequestListAgreementsPaginateTypeDef(
    _RequiredListAgreementsRequestListAgreementsPaginateTypeDef,
    _OptionalListAgreementsRequestListAgreementsPaginateTypeDef,
):
    pass


ListCertificatesRequestListCertificatesPaginateTypeDef = TypedDict(
    "ListCertificatesRequestListCertificatesPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListConnectorsRequestListConnectorsPaginateTypeDef = TypedDict(
    "ListConnectorsRequestListConnectorsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredListExecutionsRequestListExecutionsPaginateTypeDef = TypedDict(
    "_RequiredListExecutionsRequestListExecutionsPaginateTypeDef",
    {
        "WorkflowId": str,
    },
)
_OptionalListExecutionsRequestListExecutionsPaginateTypeDef = TypedDict(
    "_OptionalListExecutionsRequestListExecutionsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class ListExecutionsRequestListExecutionsPaginateTypeDef(
    _RequiredListExecutionsRequestListExecutionsPaginateTypeDef,
    _OptionalListExecutionsRequestListExecutionsPaginateTypeDef,
):
    pass


ListProfilesRequestListProfilesPaginateTypeDef = TypedDict(
    "ListProfilesRequestListProfilesPaginateTypeDef",
    {
        "ProfileType": ProfileTypeType,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListSecurityPoliciesRequestListSecurityPoliciesPaginateTypeDef = TypedDict(
    "ListSecurityPoliciesRequestListSecurityPoliciesPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListServersRequestListServersPaginateTypeDef = TypedDict(
    "ListServersRequestListServersPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredListTagsForResourceRequestListTagsForResourcePaginateTypeDef = TypedDict(
    "_RequiredListTagsForResourceRequestListTagsForResourcePaginateTypeDef",
    {
        "Arn": str,
    },
)
_OptionalListTagsForResourceRequestListTagsForResourcePaginateTypeDef = TypedDict(
    "_OptionalListTagsForResourceRequestListTagsForResourcePaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class ListTagsForResourceRequestListTagsForResourcePaginateTypeDef(
    _RequiredListTagsForResourceRequestListTagsForResourcePaginateTypeDef,
    _OptionalListTagsForResourceRequestListTagsForResourcePaginateTypeDef,
):
    pass


_RequiredListUsersRequestListUsersPaginateTypeDef = TypedDict(
    "_RequiredListUsersRequestListUsersPaginateTypeDef",
    {
        "ServerId": str,
    },
)
_OptionalListUsersRequestListUsersPaginateTypeDef = TypedDict(
    "_OptionalListUsersRequestListUsersPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class ListUsersRequestListUsersPaginateTypeDef(
    _RequiredListUsersRequestListUsersPaginateTypeDef,
    _OptionalListUsersRequestListUsersPaginateTypeDef,
):
    pass


ListWorkflowsRequestListWorkflowsPaginateTypeDef = TypedDict(
    "ListWorkflowsRequestListWorkflowsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListAccessesResponseTypeDef = TypedDict(
    "ListAccessesResponseTypeDef",
    {
        "NextToken": str,
        "ServerId": str,
        "Accesses": List[ListedAccessTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListAgreementsResponseTypeDef = TypedDict(
    "ListAgreementsResponseTypeDef",
    {
        "NextToken": str,
        "Agreements": List[ListedAgreementTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListCertificatesResponseTypeDef = TypedDict(
    "ListCertificatesResponseTypeDef",
    {
        "NextToken": str,
        "Certificates": List[ListedCertificateTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListConnectorsResponseTypeDef = TypedDict(
    "ListConnectorsResponseTypeDef",
    {
        "NextToken": str,
        "Connectors": List[ListedConnectorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListHostKeysResponseTypeDef = TypedDict(
    "ListHostKeysResponseTypeDef",
    {
        "NextToken": str,
        "ServerId": str,
        "HostKeys": List[ListedHostKeyTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListProfilesResponseTypeDef = TypedDict(
    "ListProfilesResponseTypeDef",
    {
        "NextToken": str,
        "Profiles": List[ListedProfileTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListServersResponseTypeDef = TypedDict(
    "ListServersResponseTypeDef",
    {
        "NextToken": str,
        "Servers": List[ListedServerTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListUsersResponseTypeDef = TypedDict(
    "ListUsersResponseTypeDef",
    {
        "NextToken": str,
        "ServerId": str,
        "Users": List[ListedUserTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListWorkflowsResponseTypeDef = TypedDict(
    "ListWorkflowsResponseTypeDef",
    {
        "NextToken": str,
        "Workflows": List[ListedWorkflowTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TagStepDetailsTypeDef = TypedDict(
    "TagStepDetailsTypeDef",
    {
        "Name": str,
        "Tags": Sequence[S3TagTypeDef],
        "SourceFileLocation": str,
    },
    total=False,
)

ServiceMetadataTypeDef = TypedDict(
    "ServiceMetadataTypeDef",
    {
        "UserDetails": UserDetailsTypeDef,
    },
)

WorkflowDetailsTypeDef = TypedDict(
    "WorkflowDetailsTypeDef",
    {
        "OnUpload": Sequence[WorkflowDetailTypeDef],
        "OnPartialUpload": Sequence[WorkflowDetailTypeDef],
    },
    total=False,
)

DescribeAccessResponseTypeDef = TypedDict(
    "DescribeAccessResponseTypeDef",
    {
        "ServerId": str,
        "Access": DescribedAccessTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeAgreementResponseTypeDef = TypedDict(
    "DescribeAgreementResponseTypeDef",
    {
        "Agreement": DescribedAgreementTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeCertificateResponseTypeDef = TypedDict(
    "DescribeCertificateResponseTypeDef",
    {
        "Certificate": DescribedCertificateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeConnectorResponseTypeDef = TypedDict(
    "DescribeConnectorResponseTypeDef",
    {
        "Connector": DescribedConnectorTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeHostKeyResponseTypeDef = TypedDict(
    "DescribeHostKeyResponseTypeDef",
    {
        "HostKey": DescribedHostKeyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeProfileResponseTypeDef = TypedDict(
    "DescribeProfileResponseTypeDef",
    {
        "Profile": DescribedProfileTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeUserResponseTypeDef = TypedDict(
    "DescribeUserResponseTypeDef",
    {
        "ServerId": str,
        "User": DescribedUserTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ExecutionResultsTypeDef = TypedDict(
    "ExecutionResultsTypeDef",
    {
        "Steps": List[ExecutionStepResultTypeDef],
        "OnExceptionSteps": List[ExecutionStepResultTypeDef],
    },
    total=False,
)

CopyStepDetailsTypeDef = TypedDict(
    "CopyStepDetailsTypeDef",
    {
        "Name": str,
        "DestinationFileLocation": InputFileLocationTypeDef,
        "OverwriteExisting": OverwriteExistingType,
        "SourceFileLocation": str,
    },
    total=False,
)

_RequiredDecryptStepDetailsTypeDef = TypedDict(
    "_RequiredDecryptStepDetailsTypeDef",
    {
        "Type": Literal["PGP"],
        "DestinationFileLocation": InputFileLocationTypeDef,
    },
)
_OptionalDecryptStepDetailsTypeDef = TypedDict(
    "_OptionalDecryptStepDetailsTypeDef",
    {
        "Name": str,
        "SourceFileLocation": str,
        "OverwriteExisting": OverwriteExistingType,
    },
    total=False,
)


class DecryptStepDetailsTypeDef(
    _RequiredDecryptStepDetailsTypeDef, _OptionalDecryptStepDetailsTypeDef
):
    pass


ListedExecutionTypeDef = TypedDict(
    "ListedExecutionTypeDef",
    {
        "ExecutionId": str,
        "InitialFileLocation": FileLocationTypeDef,
        "ServiceMetadata": ServiceMetadataTypeDef,
        "Status": ExecutionStatusType,
    },
    total=False,
)

CreateServerRequestRequestTypeDef = TypedDict(
    "CreateServerRequestRequestTypeDef",
    {
        "Certificate": str,
        "Domain": DomainType,
        "EndpointDetails": EndpointDetailsTypeDef,
        "EndpointType": EndpointTypeType,
        "HostKey": str,
        "IdentityProviderDetails": IdentityProviderDetailsTypeDef,
        "IdentityProviderType": IdentityProviderTypeType,
        "LoggingRole": str,
        "PostAuthenticationLoginBanner": str,
        "PreAuthenticationLoginBanner": str,
        "Protocols": Sequence[ProtocolType],
        "ProtocolDetails": ProtocolDetailsTypeDef,
        "SecurityPolicyName": str,
        "Tags": Sequence[TagTypeDef],
        "WorkflowDetails": WorkflowDetailsTypeDef,
    },
    total=False,
)

_RequiredDescribedServerTypeDef = TypedDict(
    "_RequiredDescribedServerTypeDef",
    {
        "Arn": str,
    },
)
_OptionalDescribedServerTypeDef = TypedDict(
    "_OptionalDescribedServerTypeDef",
    {
        "Certificate": str,
        "ProtocolDetails": ProtocolDetailsTypeDef,
        "Domain": DomainType,
        "EndpointDetails": EndpointDetailsTypeDef,
        "EndpointType": EndpointTypeType,
        "HostKeyFingerprint": str,
        "IdentityProviderDetails": IdentityProviderDetailsTypeDef,
        "IdentityProviderType": IdentityProviderTypeType,
        "LoggingRole": str,
        "PostAuthenticationLoginBanner": str,
        "PreAuthenticationLoginBanner": str,
        "Protocols": List[ProtocolType],
        "SecurityPolicyName": str,
        "ServerId": str,
        "State": StateType,
        "Tags": List[TagTypeDef],
        "UserCount": int,
        "WorkflowDetails": WorkflowDetailsTypeDef,
    },
    total=False,
)


class DescribedServerTypeDef(_RequiredDescribedServerTypeDef, _OptionalDescribedServerTypeDef):
    pass


_RequiredUpdateServerRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateServerRequestRequestTypeDef",
    {
        "ServerId": str,
    },
)
_OptionalUpdateServerRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateServerRequestRequestTypeDef",
    {
        "Certificate": str,
        "ProtocolDetails": ProtocolDetailsTypeDef,
        "EndpointDetails": EndpointDetailsTypeDef,
        "EndpointType": EndpointTypeType,
        "HostKey": str,
        "IdentityProviderDetails": IdentityProviderDetailsTypeDef,
        "LoggingRole": str,
        "PostAuthenticationLoginBanner": str,
        "PreAuthenticationLoginBanner": str,
        "Protocols": Sequence[ProtocolType],
        "SecurityPolicyName": str,
        "WorkflowDetails": WorkflowDetailsTypeDef,
    },
    total=False,
)


class UpdateServerRequestRequestTypeDef(
    _RequiredUpdateServerRequestRequestTypeDef, _OptionalUpdateServerRequestRequestTypeDef
):
    pass


DescribedExecutionTypeDef = TypedDict(
    "DescribedExecutionTypeDef",
    {
        "ExecutionId": str,
        "InitialFileLocation": FileLocationTypeDef,
        "ServiceMetadata": ServiceMetadataTypeDef,
        "ExecutionRole": str,
        "LoggingConfiguration": LoggingConfigurationTypeDef,
        "PosixProfile": PosixProfileTypeDef,
        "Status": ExecutionStatusType,
        "Results": ExecutionResultsTypeDef,
    },
    total=False,
)

WorkflowStepTypeDef = TypedDict(
    "WorkflowStepTypeDef",
    {
        "Type": WorkflowStepTypeType,
        "CopyStepDetails": CopyStepDetailsTypeDef,
        "CustomStepDetails": CustomStepDetailsTypeDef,
        "DeleteStepDetails": DeleteStepDetailsTypeDef,
        "TagStepDetails": TagStepDetailsTypeDef,
        "DecryptStepDetails": DecryptStepDetailsTypeDef,
    },
    total=False,
)

ListExecutionsResponseTypeDef = TypedDict(
    "ListExecutionsResponseTypeDef",
    {
        "NextToken": str,
        "WorkflowId": str,
        "Executions": List[ListedExecutionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeServerResponseTypeDef = TypedDict(
    "DescribeServerResponseTypeDef",
    {
        "Server": DescribedServerTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeExecutionResponseTypeDef = TypedDict(
    "DescribeExecutionResponseTypeDef",
    {
        "WorkflowId": str,
        "Execution": DescribedExecutionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCreateWorkflowRequestRequestTypeDef = TypedDict(
    "_RequiredCreateWorkflowRequestRequestTypeDef",
    {
        "Steps": Sequence[WorkflowStepTypeDef],
    },
)
_OptionalCreateWorkflowRequestRequestTypeDef = TypedDict(
    "_OptionalCreateWorkflowRequestRequestTypeDef",
    {
        "Description": str,
        "OnExceptionSteps": Sequence[WorkflowStepTypeDef],
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateWorkflowRequestRequestTypeDef(
    _RequiredCreateWorkflowRequestRequestTypeDef, _OptionalCreateWorkflowRequestRequestTypeDef
):
    pass


_RequiredDescribedWorkflowTypeDef = TypedDict(
    "_RequiredDescribedWorkflowTypeDef",
    {
        "Arn": str,
    },
)
_OptionalDescribedWorkflowTypeDef = TypedDict(
    "_OptionalDescribedWorkflowTypeDef",
    {
        "Description": str,
        "Steps": List[WorkflowStepTypeDef],
        "OnExceptionSteps": List[WorkflowStepTypeDef],
        "WorkflowId": str,
        "Tags": List[TagTypeDef],
    },
    total=False,
)


class DescribedWorkflowTypeDef(
    _RequiredDescribedWorkflowTypeDef, _OptionalDescribedWorkflowTypeDef
):
    pass


DescribeWorkflowResponseTypeDef = TypedDict(
    "DescribeWorkflowResponseTypeDef",
    {
        "Workflow": DescribedWorkflowTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
