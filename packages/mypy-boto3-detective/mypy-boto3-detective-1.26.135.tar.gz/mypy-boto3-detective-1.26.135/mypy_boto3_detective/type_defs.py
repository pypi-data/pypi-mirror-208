"""
Type annotations for detective service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_detective/type_defs/)

Usage::

    ```python
    from mypy_boto3_detective.type_defs import AcceptInvitationRequestRequestTypeDef

    data: AcceptInvitationRequestRequestTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import (
    DatasourcePackageIngestStateType,
    DatasourcePackageType,
    InvitationTypeType,
    MemberDisabledReasonType,
    MemberStatusType,
)

if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "AcceptInvitationRequestRequestTypeDef",
    "AccountTypeDef",
    "AdministratorTypeDef",
    "BatchGetGraphMemberDatasourcesRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "UnprocessedAccountTypeDef",
    "BatchGetMembershipDatasourcesRequestRequestTypeDef",
    "UnprocessedGraphTypeDef",
    "CreateGraphRequestRequestTypeDef",
    "TimestampForCollectionTypeDef",
    "DatasourcePackageUsageInfoTypeDef",
    "DeleteGraphRequestRequestTypeDef",
    "DeleteMembersRequestRequestTypeDef",
    "DescribeOrganizationConfigurationRequestRequestTypeDef",
    "DisassociateMembershipRequestRequestTypeDef",
    "EnableOrganizationAdminAccountRequestRequestTypeDef",
    "GetMembersRequestRequestTypeDef",
    "GraphTypeDef",
    "ListDatasourcePackagesRequestRequestTypeDef",
    "ListGraphsRequestRequestTypeDef",
    "ListInvitationsRequestRequestTypeDef",
    "ListMembersRequestRequestTypeDef",
    "ListOrganizationAdminAccountsRequestRequestTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "RejectInvitationRequestRequestTypeDef",
    "StartMonitoringMemberRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateDatasourcePackagesRequestRequestTypeDef",
    "UpdateOrganizationConfigurationRequestRequestTypeDef",
    "CreateMembersRequestRequestTypeDef",
    "CreateGraphResponseTypeDef",
    "DescribeOrganizationConfigurationResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "ListOrganizationAdminAccountsResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "DeleteMembersResponseTypeDef",
    "DatasourcePackageIngestDetailTypeDef",
    "MembershipDatasourcesTypeDef",
    "MemberDetailTypeDef",
    "ListGraphsResponseTypeDef",
    "ListDatasourcePackagesResponseTypeDef",
    "BatchGetGraphMemberDatasourcesResponseTypeDef",
    "BatchGetMembershipDatasourcesResponseTypeDef",
    "CreateMembersResponseTypeDef",
    "GetMembersResponseTypeDef",
    "ListInvitationsResponseTypeDef",
    "ListMembersResponseTypeDef",
)

AcceptInvitationRequestRequestTypeDef = TypedDict(
    "AcceptInvitationRequestRequestTypeDef",
    {
        "GraphArn": str,
    },
)

AccountTypeDef = TypedDict(
    "AccountTypeDef",
    {
        "AccountId": str,
        "EmailAddress": str,
    },
)

AdministratorTypeDef = TypedDict(
    "AdministratorTypeDef",
    {
        "AccountId": str,
        "GraphArn": str,
        "DelegationTime": datetime,
    },
    total=False,
)

BatchGetGraphMemberDatasourcesRequestRequestTypeDef = TypedDict(
    "BatchGetGraphMemberDatasourcesRequestRequestTypeDef",
    {
        "GraphArn": str,
        "AccountIds": Sequence[str],
    },
)

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

UnprocessedAccountTypeDef = TypedDict(
    "UnprocessedAccountTypeDef",
    {
        "AccountId": str,
        "Reason": str,
    },
    total=False,
)

BatchGetMembershipDatasourcesRequestRequestTypeDef = TypedDict(
    "BatchGetMembershipDatasourcesRequestRequestTypeDef",
    {
        "GraphArns": Sequence[str],
    },
)

UnprocessedGraphTypeDef = TypedDict(
    "UnprocessedGraphTypeDef",
    {
        "GraphArn": str,
        "Reason": str,
    },
    total=False,
)

CreateGraphRequestRequestTypeDef = TypedDict(
    "CreateGraphRequestRequestTypeDef",
    {
        "Tags": Mapping[str, str],
    },
    total=False,
)

TimestampForCollectionTypeDef = TypedDict(
    "TimestampForCollectionTypeDef",
    {
        "Timestamp": datetime,
    },
    total=False,
)

DatasourcePackageUsageInfoTypeDef = TypedDict(
    "DatasourcePackageUsageInfoTypeDef",
    {
        "VolumeUsageInBytes": int,
        "VolumeUsageUpdateTime": datetime,
    },
    total=False,
)

DeleteGraphRequestRequestTypeDef = TypedDict(
    "DeleteGraphRequestRequestTypeDef",
    {
        "GraphArn": str,
    },
)

DeleteMembersRequestRequestTypeDef = TypedDict(
    "DeleteMembersRequestRequestTypeDef",
    {
        "GraphArn": str,
        "AccountIds": Sequence[str],
    },
)

DescribeOrganizationConfigurationRequestRequestTypeDef = TypedDict(
    "DescribeOrganizationConfigurationRequestRequestTypeDef",
    {
        "GraphArn": str,
    },
)

DisassociateMembershipRequestRequestTypeDef = TypedDict(
    "DisassociateMembershipRequestRequestTypeDef",
    {
        "GraphArn": str,
    },
)

EnableOrganizationAdminAccountRequestRequestTypeDef = TypedDict(
    "EnableOrganizationAdminAccountRequestRequestTypeDef",
    {
        "AccountId": str,
    },
)

GetMembersRequestRequestTypeDef = TypedDict(
    "GetMembersRequestRequestTypeDef",
    {
        "GraphArn": str,
        "AccountIds": Sequence[str],
    },
)

GraphTypeDef = TypedDict(
    "GraphTypeDef",
    {
        "Arn": str,
        "CreatedTime": datetime,
    },
    total=False,
)

_RequiredListDatasourcePackagesRequestRequestTypeDef = TypedDict(
    "_RequiredListDatasourcePackagesRequestRequestTypeDef",
    {
        "GraphArn": str,
    },
)
_OptionalListDatasourcePackagesRequestRequestTypeDef = TypedDict(
    "_OptionalListDatasourcePackagesRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)


class ListDatasourcePackagesRequestRequestTypeDef(
    _RequiredListDatasourcePackagesRequestRequestTypeDef,
    _OptionalListDatasourcePackagesRequestRequestTypeDef,
):
    pass


ListGraphsRequestRequestTypeDef = TypedDict(
    "ListGraphsRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListInvitationsRequestRequestTypeDef = TypedDict(
    "ListInvitationsRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

_RequiredListMembersRequestRequestTypeDef = TypedDict(
    "_RequiredListMembersRequestRequestTypeDef",
    {
        "GraphArn": str,
    },
)
_OptionalListMembersRequestRequestTypeDef = TypedDict(
    "_OptionalListMembersRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)


class ListMembersRequestRequestTypeDef(
    _RequiredListMembersRequestRequestTypeDef, _OptionalListMembersRequestRequestTypeDef
):
    pass


ListOrganizationAdminAccountsRequestRequestTypeDef = TypedDict(
    "ListOrganizationAdminAccountsRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)

RejectInvitationRequestRequestTypeDef = TypedDict(
    "RejectInvitationRequestRequestTypeDef",
    {
        "GraphArn": str,
    },
)

StartMonitoringMemberRequestRequestTypeDef = TypedDict(
    "StartMonitoringMemberRequestRequestTypeDef",
    {
        "GraphArn": str,
        "AccountId": str,
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "Tags": Mapping[str, str],
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "TagKeys": Sequence[str],
    },
)

UpdateDatasourcePackagesRequestRequestTypeDef = TypedDict(
    "UpdateDatasourcePackagesRequestRequestTypeDef",
    {
        "GraphArn": str,
        "DatasourcePackages": Sequence[DatasourcePackageType],
    },
)

_RequiredUpdateOrganizationConfigurationRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateOrganizationConfigurationRequestRequestTypeDef",
    {
        "GraphArn": str,
    },
)
_OptionalUpdateOrganizationConfigurationRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateOrganizationConfigurationRequestRequestTypeDef",
    {
        "AutoEnable": bool,
    },
    total=False,
)


class UpdateOrganizationConfigurationRequestRequestTypeDef(
    _RequiredUpdateOrganizationConfigurationRequestRequestTypeDef,
    _OptionalUpdateOrganizationConfigurationRequestRequestTypeDef,
):
    pass


_RequiredCreateMembersRequestRequestTypeDef = TypedDict(
    "_RequiredCreateMembersRequestRequestTypeDef",
    {
        "GraphArn": str,
        "Accounts": Sequence[AccountTypeDef],
    },
)
_OptionalCreateMembersRequestRequestTypeDef = TypedDict(
    "_OptionalCreateMembersRequestRequestTypeDef",
    {
        "Message": str,
        "DisableEmailNotification": bool,
    },
    total=False,
)


class CreateMembersRequestRequestTypeDef(
    _RequiredCreateMembersRequestRequestTypeDef, _OptionalCreateMembersRequestRequestTypeDef
):
    pass


CreateGraphResponseTypeDef = TypedDict(
    "CreateGraphResponseTypeDef",
    {
        "GraphArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeOrganizationConfigurationResponseTypeDef = TypedDict(
    "DescribeOrganizationConfigurationResponseTypeDef",
    {
        "AutoEnable": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListOrganizationAdminAccountsResponseTypeDef = TypedDict(
    "ListOrganizationAdminAccountsResponseTypeDef",
    {
        "Administrators": List[AdministratorTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteMembersResponseTypeDef = TypedDict(
    "DeleteMembersResponseTypeDef",
    {
        "AccountIds": List[str],
        "UnprocessedAccounts": List[UnprocessedAccountTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DatasourcePackageIngestDetailTypeDef = TypedDict(
    "DatasourcePackageIngestDetailTypeDef",
    {
        "DatasourcePackageIngestState": DatasourcePackageIngestStateType,
        "LastIngestStateChange": Dict[
            DatasourcePackageIngestStateType, TimestampForCollectionTypeDef
        ],
    },
    total=False,
)

MembershipDatasourcesTypeDef = TypedDict(
    "MembershipDatasourcesTypeDef",
    {
        "AccountId": str,
        "GraphArn": str,
        "DatasourcePackageIngestHistory": Dict[
            DatasourcePackageType,
            Dict[DatasourcePackageIngestStateType, TimestampForCollectionTypeDef],
        ],
    },
    total=False,
)

MemberDetailTypeDef = TypedDict(
    "MemberDetailTypeDef",
    {
        "AccountId": str,
        "EmailAddress": str,
        "GraphArn": str,
        "MasterId": str,
        "AdministratorId": str,
        "Status": MemberStatusType,
        "DisabledReason": MemberDisabledReasonType,
        "InvitedTime": datetime,
        "UpdatedTime": datetime,
        "VolumeUsageInBytes": int,
        "VolumeUsageUpdatedTime": datetime,
        "PercentOfGraphUtilization": float,
        "PercentOfGraphUtilizationUpdatedTime": datetime,
        "InvitationType": InvitationTypeType,
        "VolumeUsageByDatasourcePackage": Dict[
            DatasourcePackageType, DatasourcePackageUsageInfoTypeDef
        ],
        "DatasourcePackageIngestStates": Dict[
            DatasourcePackageType, DatasourcePackageIngestStateType
        ],
    },
    total=False,
)

ListGraphsResponseTypeDef = TypedDict(
    "ListGraphsResponseTypeDef",
    {
        "GraphList": List[GraphTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListDatasourcePackagesResponseTypeDef = TypedDict(
    "ListDatasourcePackagesResponseTypeDef",
    {
        "DatasourcePackages": Dict[DatasourcePackageType, DatasourcePackageIngestDetailTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BatchGetGraphMemberDatasourcesResponseTypeDef = TypedDict(
    "BatchGetGraphMemberDatasourcesResponseTypeDef",
    {
        "MemberDatasources": List[MembershipDatasourcesTypeDef],
        "UnprocessedAccounts": List[UnprocessedAccountTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BatchGetMembershipDatasourcesResponseTypeDef = TypedDict(
    "BatchGetMembershipDatasourcesResponseTypeDef",
    {
        "MembershipDatasources": List[MembershipDatasourcesTypeDef],
        "UnprocessedGraphs": List[UnprocessedGraphTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateMembersResponseTypeDef = TypedDict(
    "CreateMembersResponseTypeDef",
    {
        "Members": List[MemberDetailTypeDef],
        "UnprocessedAccounts": List[UnprocessedAccountTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetMembersResponseTypeDef = TypedDict(
    "GetMembersResponseTypeDef",
    {
        "MemberDetails": List[MemberDetailTypeDef],
        "UnprocessedAccounts": List[UnprocessedAccountTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListInvitationsResponseTypeDef = TypedDict(
    "ListInvitationsResponseTypeDef",
    {
        "Invitations": List[MemberDetailTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListMembersResponseTypeDef = TypedDict(
    "ListMembersResponseTypeDef",
    {
        "MemberDetails": List[MemberDetailTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
