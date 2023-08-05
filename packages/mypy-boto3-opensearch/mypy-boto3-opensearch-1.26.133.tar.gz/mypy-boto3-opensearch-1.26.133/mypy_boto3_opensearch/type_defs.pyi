"""
Type annotations for opensearch service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_opensearch/type_defs/)

Usage::

    ```python
    from mypy_boto3_opensearch.type_defs import AWSDomainInformationTypeDef

    data: AWSDomainInformationTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence, Union

from .literals import (
    ActionSeverityType,
    ActionStatusType,
    ActionTypeType,
    AutoTuneDesiredStateType,
    AutoTuneStateType,
    ConnectionModeType,
    DeploymentStatusType,
    DescribePackagesFilterNameType,
    DomainHealthType,
    DomainPackageStatusType,
    DomainStateType,
    DryRunModeType,
    EngineTypeType,
    InboundConnectionStatusCodeType,
    LogTypeType,
    MasterNodeStatusType,
    NodeStatusType,
    NodeTypeType,
    OpenSearchPartitionInstanceTypeType,
    OpenSearchWarmPartitionInstanceTypeType,
    OptionStateType,
    OutboundConnectionStatusCodeType,
    OverallChangeStatusType,
    PackageStatusType,
    PrincipalTypeType,
    ReservedInstancePaymentOptionType,
    RollbackOnDisableType,
    ScheduleAtType,
    ScheduledAutoTuneActionTypeType,
    ScheduledAutoTuneSeverityTypeType,
    ScheduledByType,
    TLSSecurityPolicyType,
    UpgradeStatusType,
    UpgradeStepType,
    VolumeTypeType,
    VpcEndpointErrorCodeType,
    VpcEndpointStatusType,
    ZoneStatusType,
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
    "AWSDomainInformationTypeDef",
    "AcceptInboundConnectionRequestRequestTypeDef",
    "OptionStatusTypeDef",
    "TagTypeDef",
    "AdditionalLimitTypeDef",
    "MasterUserOptionsTypeDef",
    "AssociatePackageRequestRequestTypeDef",
    "AuthorizeVpcEndpointAccessRequestRequestTypeDef",
    "AuthorizedPrincipalTypeDef",
    "ScheduledAutoTuneDetailsTypeDef",
    "DurationTypeDef",
    "AutoTuneOptionsOutputTypeDef",
    "AutoTuneStatusTypeDef",
    "AvailabilityZoneInfoTypeDef",
    "CancelServiceSoftwareUpdateRequestRequestTypeDef",
    "ServiceSoftwareOptionsTypeDef",
    "ChangeProgressDetailsTypeDef",
    "ChangeProgressStageTypeDef",
    "ColdStorageOptionsTypeDef",
    "ZoneAwarenessConfigTypeDef",
    "CognitoOptionsTypeDef",
    "CompatibleVersionsMapTypeDef",
    "ConnectionPropertiesTypeDef",
    "DomainEndpointOptionsTypeDef",
    "EBSOptionsTypeDef",
    "EncryptionAtRestOptionsTypeDef",
    "LogPublishingOptionTypeDef",
    "NodeToNodeEncryptionOptionsTypeDef",
    "SnapshotOptionsTypeDef",
    "SoftwareUpdateOptionsTypeDef",
    "VPCOptionsTypeDef",
    "OutboundConnectionStatusTypeDef",
    "PackageSourceTypeDef",
    "DeleteDomainRequestRequestTypeDef",
    "DeleteInboundConnectionRequestRequestTypeDef",
    "DeleteOutboundConnectionRequestRequestTypeDef",
    "DeletePackageRequestRequestTypeDef",
    "DeleteVpcEndpointRequestRequestTypeDef",
    "VpcEndpointSummaryTypeDef",
    "DescribeDomainAutoTunesRequestRequestTypeDef",
    "DescribeDomainChangeProgressRequestRequestTypeDef",
    "DescribeDomainConfigRequestRequestTypeDef",
    "DescribeDomainHealthRequestRequestTypeDef",
    "DescribeDomainNodesRequestRequestTypeDef",
    "DomainNodesStatusTypeDef",
    "DescribeDomainRequestRequestTypeDef",
    "DescribeDomainsRequestRequestTypeDef",
    "DescribeDryRunProgressRequestRequestTypeDef",
    "DryRunResultsTypeDef",
    "FilterTypeDef",
    "DescribeInstanceTypeLimitsRequestRequestTypeDef",
    "DescribePackagesFilterTypeDef",
    "DescribeReservedInstanceOfferingsRequestRequestTypeDef",
    "DescribeReservedInstancesRequestRequestTypeDef",
    "DescribeVpcEndpointsRequestRequestTypeDef",
    "VpcEndpointErrorTypeDef",
    "DissociatePackageRequestRequestTypeDef",
    "DomainInfoTypeDef",
    "ErrorDetailsTypeDef",
    "VPCDerivedInfoTypeDef",
    "ValidationFailureTypeDef",
    "EmptyResponseMetadataTypeDef",
    "GetCompatibleVersionsRequestRequestTypeDef",
    "GetPackageVersionHistoryRequestRequestTypeDef",
    "PackageVersionHistoryTypeDef",
    "GetUpgradeHistoryRequestRequestTypeDef",
    "GetUpgradeStatusRequestRequestTypeDef",
    "GetUpgradeStatusResponseTypeDef",
    "InboundConnectionStatusTypeDef",
    "InstanceCountLimitsTypeDef",
    "InstanceTypeDetailsTypeDef",
    "ListDomainNamesRequestRequestTypeDef",
    "ListDomainsForPackageRequestRequestTypeDef",
    "ListInstanceTypeDetailsRequestRequestTypeDef",
    "ListPackagesForDomainRequestRequestTypeDef",
    "ListScheduledActionsRequestRequestTypeDef",
    "ScheduledActionTypeDef",
    "ListTagsRequestRequestTypeDef",
    "ListVersionsRequestRequestTypeDef",
    "ListVersionsResponseTypeDef",
    "ListVpcEndpointAccessRequestRequestTypeDef",
    "ListVpcEndpointsForDomainRequestRequestTypeDef",
    "ListVpcEndpointsRequestRequestTypeDef",
    "WindowStartTimeTypeDef",
    "PurchaseReservedInstanceOfferingRequestRequestTypeDef",
    "PurchaseReservedInstanceOfferingResponseTypeDef",
    "RecurringChargeTypeDef",
    "RejectInboundConnectionRequestRequestTypeDef",
    "RemoveTagsRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "RevokeVpcEndpointAccessRequestRequestTypeDef",
    "SAMLIdpTypeDef",
    "StartServiceSoftwareUpdateRequestRequestTypeDef",
    "StorageTypeLimitTypeDef",
    "UpdateScheduledActionRequestRequestTypeDef",
    "UpgradeDomainRequestRequestTypeDef",
    "UpgradeStepItemTypeDef",
    "DomainInformationContainerTypeDef",
    "AccessPoliciesStatusTypeDef",
    "AdvancedOptionsStatusTypeDef",
    "VersionStatusTypeDef",
    "AddTagsRequestRequestTypeDef",
    "ListTagsResponseTypeDef",
    "AuthorizeVpcEndpointAccessResponseTypeDef",
    "ListVpcEndpointAccessResponseTypeDef",
    "AutoTuneDetailsTypeDef",
    "AutoTuneMaintenanceScheduleTypeDef",
    "EnvironmentInfoTypeDef",
    "CancelServiceSoftwareUpdateResponseTypeDef",
    "StartServiceSoftwareUpdateResponseTypeDef",
    "UpgradeDomainResponseTypeDef",
    "ChangeProgressStatusDetailsTypeDef",
    "ClusterConfigTypeDef",
    "CognitoOptionsStatusTypeDef",
    "GetCompatibleVersionsResponseTypeDef",
    "DomainEndpointOptionsStatusTypeDef",
    "EBSOptionsStatusTypeDef",
    "EncryptionAtRestOptionsStatusTypeDef",
    "LogPublishingOptionsStatusTypeDef",
    "NodeToNodeEncryptionOptionsStatusTypeDef",
    "SnapshotOptionsStatusTypeDef",
    "SoftwareUpdateOptionsStatusTypeDef",
    "CreateVpcEndpointRequestRequestTypeDef",
    "UpdateVpcEndpointRequestRequestTypeDef",
    "CreatePackageRequestRequestTypeDef",
    "UpdatePackageRequestRequestTypeDef",
    "DeleteVpcEndpointResponseTypeDef",
    "ListVpcEndpointsForDomainResponseTypeDef",
    "ListVpcEndpointsResponseTypeDef",
    "DescribeDomainNodesResponseTypeDef",
    "DescribeInboundConnectionsRequestRequestTypeDef",
    "DescribeOutboundConnectionsRequestRequestTypeDef",
    "DescribePackagesRequestRequestTypeDef",
    "ListDomainNamesResponseTypeDef",
    "DomainPackageDetailsTypeDef",
    "PackageDetailsTypeDef",
    "VPCDerivedInfoStatusTypeDef",
    "VpcEndpointTypeDef",
    "DryRunProgressStatusTypeDef",
    "GetPackageVersionHistoryResponseTypeDef",
    "InstanceLimitsTypeDef",
    "ListInstanceTypeDetailsResponseTypeDef",
    "ListScheduledActionsResponseTypeDef",
    "UpdateScheduledActionResponseTypeDef",
    "OffPeakWindowTypeDef",
    "ReservedInstanceOfferingTypeDef",
    "ReservedInstanceTypeDef",
    "SAMLOptionsInputTypeDef",
    "SAMLOptionsOutputTypeDef",
    "StorageTypeTypeDef",
    "UpgradeHistoryTypeDef",
    "CreateOutboundConnectionRequestRequestTypeDef",
    "CreateOutboundConnectionResponseTypeDef",
    "InboundConnectionTypeDef",
    "OutboundConnectionTypeDef",
    "AutoTuneTypeDef",
    "AutoTuneOptionsInputTypeDef",
    "AutoTuneOptionsTypeDef",
    "DescribeDomainHealthResponseTypeDef",
    "DescribeDomainChangeProgressResponseTypeDef",
    "ClusterConfigStatusTypeDef",
    "AssociatePackageResponseTypeDef",
    "DissociatePackageResponseTypeDef",
    "ListDomainsForPackageResponseTypeDef",
    "ListPackagesForDomainResponseTypeDef",
    "CreatePackageResponseTypeDef",
    "DeletePackageResponseTypeDef",
    "DescribePackagesResponseTypeDef",
    "UpdatePackageResponseTypeDef",
    "CreateVpcEndpointResponseTypeDef",
    "DescribeVpcEndpointsResponseTypeDef",
    "UpdateVpcEndpointResponseTypeDef",
    "OffPeakWindowOptionsTypeDef",
    "DescribeReservedInstanceOfferingsResponseTypeDef",
    "DescribeReservedInstancesResponseTypeDef",
    "AdvancedSecurityOptionsInputTypeDef",
    "AdvancedSecurityOptionsTypeDef",
    "LimitsTypeDef",
    "GetUpgradeHistoryResponseTypeDef",
    "AcceptInboundConnectionResponseTypeDef",
    "DeleteInboundConnectionResponseTypeDef",
    "DescribeInboundConnectionsResponseTypeDef",
    "RejectInboundConnectionResponseTypeDef",
    "DeleteOutboundConnectionResponseTypeDef",
    "DescribeOutboundConnectionsResponseTypeDef",
    "DescribeDomainAutoTunesResponseTypeDef",
    "AutoTuneOptionsStatusTypeDef",
    "OffPeakWindowOptionsStatusTypeDef",
    "CreateDomainRequestRequestTypeDef",
    "UpdateDomainConfigRequestRequestTypeDef",
    "AdvancedSecurityOptionsStatusTypeDef",
    "DomainStatusTypeDef",
    "DescribeInstanceTypeLimitsResponseTypeDef",
    "DomainConfigTypeDef",
    "CreateDomainResponseTypeDef",
    "DeleteDomainResponseTypeDef",
    "DescribeDomainResponseTypeDef",
    "DescribeDomainsResponseTypeDef",
    "DescribeDryRunProgressResponseTypeDef",
    "DescribeDomainConfigResponseTypeDef",
    "UpdateDomainConfigResponseTypeDef",
)

_RequiredAWSDomainInformationTypeDef = TypedDict(
    "_RequiredAWSDomainInformationTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalAWSDomainInformationTypeDef = TypedDict(
    "_OptionalAWSDomainInformationTypeDef",
    {
        "OwnerId": str,
        "Region": str,
    },
    total=False,
)

class AWSDomainInformationTypeDef(
    _RequiredAWSDomainInformationTypeDef, _OptionalAWSDomainInformationTypeDef
):
    pass

AcceptInboundConnectionRequestRequestTypeDef = TypedDict(
    "AcceptInboundConnectionRequestRequestTypeDef",
    {
        "ConnectionId": str,
    },
)

_RequiredOptionStatusTypeDef = TypedDict(
    "_RequiredOptionStatusTypeDef",
    {
        "CreationDate": datetime,
        "UpdateDate": datetime,
        "State": OptionStateType,
    },
)
_OptionalOptionStatusTypeDef = TypedDict(
    "_OptionalOptionStatusTypeDef",
    {
        "UpdateVersion": int,
        "PendingDeletion": bool,
    },
    total=False,
)

class OptionStatusTypeDef(_RequiredOptionStatusTypeDef, _OptionalOptionStatusTypeDef):
    pass

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)

AdditionalLimitTypeDef = TypedDict(
    "AdditionalLimitTypeDef",
    {
        "LimitName": str,
        "LimitValues": List[str],
    },
    total=False,
)

MasterUserOptionsTypeDef = TypedDict(
    "MasterUserOptionsTypeDef",
    {
        "MasterUserARN": str,
        "MasterUserName": str,
        "MasterUserPassword": str,
    },
    total=False,
)

AssociatePackageRequestRequestTypeDef = TypedDict(
    "AssociatePackageRequestRequestTypeDef",
    {
        "PackageID": str,
        "DomainName": str,
    },
)

AuthorizeVpcEndpointAccessRequestRequestTypeDef = TypedDict(
    "AuthorizeVpcEndpointAccessRequestRequestTypeDef",
    {
        "DomainName": str,
        "Account": str,
    },
)

AuthorizedPrincipalTypeDef = TypedDict(
    "AuthorizedPrincipalTypeDef",
    {
        "PrincipalType": PrincipalTypeType,
        "Principal": str,
    },
    total=False,
)

ScheduledAutoTuneDetailsTypeDef = TypedDict(
    "ScheduledAutoTuneDetailsTypeDef",
    {
        "Date": datetime,
        "ActionType": ScheduledAutoTuneActionTypeType,
        "Action": str,
        "Severity": ScheduledAutoTuneSeverityTypeType,
    },
    total=False,
)

DurationTypeDef = TypedDict(
    "DurationTypeDef",
    {
        "Value": int,
        "Unit": Literal["HOURS"],
    },
    total=False,
)

AutoTuneOptionsOutputTypeDef = TypedDict(
    "AutoTuneOptionsOutputTypeDef",
    {
        "State": AutoTuneStateType,
        "ErrorMessage": str,
        "UseOffPeakWindow": bool,
    },
    total=False,
)

_RequiredAutoTuneStatusTypeDef = TypedDict(
    "_RequiredAutoTuneStatusTypeDef",
    {
        "CreationDate": datetime,
        "UpdateDate": datetime,
        "State": AutoTuneStateType,
    },
)
_OptionalAutoTuneStatusTypeDef = TypedDict(
    "_OptionalAutoTuneStatusTypeDef",
    {
        "UpdateVersion": int,
        "ErrorMessage": str,
        "PendingDeletion": bool,
    },
    total=False,
)

class AutoTuneStatusTypeDef(_RequiredAutoTuneStatusTypeDef, _OptionalAutoTuneStatusTypeDef):
    pass

AvailabilityZoneInfoTypeDef = TypedDict(
    "AvailabilityZoneInfoTypeDef",
    {
        "AvailabilityZoneName": str,
        "ZoneStatus": ZoneStatusType,
        "ConfiguredDataNodeCount": str,
        "AvailableDataNodeCount": str,
        "TotalShards": str,
        "TotalUnAssignedShards": str,
    },
    total=False,
)

CancelServiceSoftwareUpdateRequestRequestTypeDef = TypedDict(
    "CancelServiceSoftwareUpdateRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)

ServiceSoftwareOptionsTypeDef = TypedDict(
    "ServiceSoftwareOptionsTypeDef",
    {
        "CurrentVersion": str,
        "NewVersion": str,
        "UpdateAvailable": bool,
        "Cancellable": bool,
        "UpdateStatus": DeploymentStatusType,
        "Description": str,
        "AutomatedUpdateDate": datetime,
        "OptionalDeployment": bool,
    },
    total=False,
)

ChangeProgressDetailsTypeDef = TypedDict(
    "ChangeProgressDetailsTypeDef",
    {
        "ChangeId": str,
        "Message": str,
    },
    total=False,
)

ChangeProgressStageTypeDef = TypedDict(
    "ChangeProgressStageTypeDef",
    {
        "Name": str,
        "Status": str,
        "Description": str,
        "LastUpdated": datetime,
    },
    total=False,
)

ColdStorageOptionsTypeDef = TypedDict(
    "ColdStorageOptionsTypeDef",
    {
        "Enabled": bool,
    },
)

ZoneAwarenessConfigTypeDef = TypedDict(
    "ZoneAwarenessConfigTypeDef",
    {
        "AvailabilityZoneCount": int,
    },
    total=False,
)

CognitoOptionsTypeDef = TypedDict(
    "CognitoOptionsTypeDef",
    {
        "Enabled": bool,
        "UserPoolId": str,
        "IdentityPoolId": str,
        "RoleArn": str,
    },
    total=False,
)

CompatibleVersionsMapTypeDef = TypedDict(
    "CompatibleVersionsMapTypeDef",
    {
        "SourceVersion": str,
        "TargetVersions": List[str],
    },
    total=False,
)

ConnectionPropertiesTypeDef = TypedDict(
    "ConnectionPropertiesTypeDef",
    {
        "Endpoint": str,
    },
    total=False,
)

DomainEndpointOptionsTypeDef = TypedDict(
    "DomainEndpointOptionsTypeDef",
    {
        "EnforceHTTPS": bool,
        "TLSSecurityPolicy": TLSSecurityPolicyType,
        "CustomEndpointEnabled": bool,
        "CustomEndpoint": str,
        "CustomEndpointCertificateArn": str,
    },
    total=False,
)

EBSOptionsTypeDef = TypedDict(
    "EBSOptionsTypeDef",
    {
        "EBSEnabled": bool,
        "VolumeType": VolumeTypeType,
        "VolumeSize": int,
        "Iops": int,
        "Throughput": int,
    },
    total=False,
)

EncryptionAtRestOptionsTypeDef = TypedDict(
    "EncryptionAtRestOptionsTypeDef",
    {
        "Enabled": bool,
        "KmsKeyId": str,
    },
    total=False,
)

LogPublishingOptionTypeDef = TypedDict(
    "LogPublishingOptionTypeDef",
    {
        "CloudWatchLogsLogGroupArn": str,
        "Enabled": bool,
    },
    total=False,
)

NodeToNodeEncryptionOptionsTypeDef = TypedDict(
    "NodeToNodeEncryptionOptionsTypeDef",
    {
        "Enabled": bool,
    },
    total=False,
)

SnapshotOptionsTypeDef = TypedDict(
    "SnapshotOptionsTypeDef",
    {
        "AutomatedSnapshotStartHour": int,
    },
    total=False,
)

SoftwareUpdateOptionsTypeDef = TypedDict(
    "SoftwareUpdateOptionsTypeDef",
    {
        "AutoSoftwareUpdateEnabled": bool,
    },
    total=False,
)

VPCOptionsTypeDef = TypedDict(
    "VPCOptionsTypeDef",
    {
        "SubnetIds": Sequence[str],
        "SecurityGroupIds": Sequence[str],
    },
    total=False,
)

OutboundConnectionStatusTypeDef = TypedDict(
    "OutboundConnectionStatusTypeDef",
    {
        "StatusCode": OutboundConnectionStatusCodeType,
        "Message": str,
    },
    total=False,
)

PackageSourceTypeDef = TypedDict(
    "PackageSourceTypeDef",
    {
        "S3BucketName": str,
        "S3Key": str,
    },
    total=False,
)

DeleteDomainRequestRequestTypeDef = TypedDict(
    "DeleteDomainRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)

DeleteInboundConnectionRequestRequestTypeDef = TypedDict(
    "DeleteInboundConnectionRequestRequestTypeDef",
    {
        "ConnectionId": str,
    },
)

DeleteOutboundConnectionRequestRequestTypeDef = TypedDict(
    "DeleteOutboundConnectionRequestRequestTypeDef",
    {
        "ConnectionId": str,
    },
)

DeletePackageRequestRequestTypeDef = TypedDict(
    "DeletePackageRequestRequestTypeDef",
    {
        "PackageID": str,
    },
)

DeleteVpcEndpointRequestRequestTypeDef = TypedDict(
    "DeleteVpcEndpointRequestRequestTypeDef",
    {
        "VpcEndpointId": str,
    },
)

VpcEndpointSummaryTypeDef = TypedDict(
    "VpcEndpointSummaryTypeDef",
    {
        "VpcEndpointId": str,
        "VpcEndpointOwner": str,
        "DomainArn": str,
        "Status": VpcEndpointStatusType,
    },
    total=False,
)

_RequiredDescribeDomainAutoTunesRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeDomainAutoTunesRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalDescribeDomainAutoTunesRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeDomainAutoTunesRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

class DescribeDomainAutoTunesRequestRequestTypeDef(
    _RequiredDescribeDomainAutoTunesRequestRequestTypeDef,
    _OptionalDescribeDomainAutoTunesRequestRequestTypeDef,
):
    pass

_RequiredDescribeDomainChangeProgressRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeDomainChangeProgressRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalDescribeDomainChangeProgressRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeDomainChangeProgressRequestRequestTypeDef",
    {
        "ChangeId": str,
    },
    total=False,
)

class DescribeDomainChangeProgressRequestRequestTypeDef(
    _RequiredDescribeDomainChangeProgressRequestRequestTypeDef,
    _OptionalDescribeDomainChangeProgressRequestRequestTypeDef,
):
    pass

DescribeDomainConfigRequestRequestTypeDef = TypedDict(
    "DescribeDomainConfigRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)

DescribeDomainHealthRequestRequestTypeDef = TypedDict(
    "DescribeDomainHealthRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)

DescribeDomainNodesRequestRequestTypeDef = TypedDict(
    "DescribeDomainNodesRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)

DomainNodesStatusTypeDef = TypedDict(
    "DomainNodesStatusTypeDef",
    {
        "NodeId": str,
        "NodeType": NodeTypeType,
        "AvailabilityZone": str,
        "InstanceType": OpenSearchPartitionInstanceTypeType,
        "NodeStatus": NodeStatusType,
        "StorageType": str,
        "StorageVolumeType": VolumeTypeType,
        "StorageSize": str,
    },
    total=False,
)

DescribeDomainRequestRequestTypeDef = TypedDict(
    "DescribeDomainRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)

DescribeDomainsRequestRequestTypeDef = TypedDict(
    "DescribeDomainsRequestRequestTypeDef",
    {
        "DomainNames": Sequence[str],
    },
)

_RequiredDescribeDryRunProgressRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeDryRunProgressRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalDescribeDryRunProgressRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeDryRunProgressRequestRequestTypeDef",
    {
        "DryRunId": str,
        "LoadDryRunConfig": bool,
    },
    total=False,
)

class DescribeDryRunProgressRequestRequestTypeDef(
    _RequiredDescribeDryRunProgressRequestRequestTypeDef,
    _OptionalDescribeDryRunProgressRequestRequestTypeDef,
):
    pass

DryRunResultsTypeDef = TypedDict(
    "DryRunResultsTypeDef",
    {
        "DeploymentType": str,
        "Message": str,
    },
    total=False,
)

FilterTypeDef = TypedDict(
    "FilterTypeDef",
    {
        "Name": str,
        "Values": Sequence[str],
    },
    total=False,
)

_RequiredDescribeInstanceTypeLimitsRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeInstanceTypeLimitsRequestRequestTypeDef",
    {
        "InstanceType": OpenSearchPartitionInstanceTypeType,
        "EngineVersion": str,
    },
)
_OptionalDescribeInstanceTypeLimitsRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeInstanceTypeLimitsRequestRequestTypeDef",
    {
        "DomainName": str,
    },
    total=False,
)

class DescribeInstanceTypeLimitsRequestRequestTypeDef(
    _RequiredDescribeInstanceTypeLimitsRequestRequestTypeDef,
    _OptionalDescribeInstanceTypeLimitsRequestRequestTypeDef,
):
    pass

DescribePackagesFilterTypeDef = TypedDict(
    "DescribePackagesFilterTypeDef",
    {
        "Name": DescribePackagesFilterNameType,
        "Value": Sequence[str],
    },
    total=False,
)

DescribeReservedInstanceOfferingsRequestRequestTypeDef = TypedDict(
    "DescribeReservedInstanceOfferingsRequestRequestTypeDef",
    {
        "ReservedInstanceOfferingId": str,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeReservedInstancesRequestRequestTypeDef = TypedDict(
    "DescribeReservedInstancesRequestRequestTypeDef",
    {
        "ReservedInstanceId": str,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeVpcEndpointsRequestRequestTypeDef = TypedDict(
    "DescribeVpcEndpointsRequestRequestTypeDef",
    {
        "VpcEndpointIds": Sequence[str],
    },
)

VpcEndpointErrorTypeDef = TypedDict(
    "VpcEndpointErrorTypeDef",
    {
        "VpcEndpointId": str,
        "ErrorCode": VpcEndpointErrorCodeType,
        "ErrorMessage": str,
    },
    total=False,
)

DissociatePackageRequestRequestTypeDef = TypedDict(
    "DissociatePackageRequestRequestTypeDef",
    {
        "PackageID": str,
        "DomainName": str,
    },
)

DomainInfoTypeDef = TypedDict(
    "DomainInfoTypeDef",
    {
        "DomainName": str,
        "EngineType": EngineTypeType,
    },
    total=False,
)

ErrorDetailsTypeDef = TypedDict(
    "ErrorDetailsTypeDef",
    {
        "ErrorType": str,
        "ErrorMessage": str,
    },
    total=False,
)

VPCDerivedInfoTypeDef = TypedDict(
    "VPCDerivedInfoTypeDef",
    {
        "VPCId": str,
        "SubnetIds": List[str],
        "AvailabilityZones": List[str],
        "SecurityGroupIds": List[str],
    },
    total=False,
)

ValidationFailureTypeDef = TypedDict(
    "ValidationFailureTypeDef",
    {
        "Code": str,
        "Message": str,
    },
    total=False,
)

EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetCompatibleVersionsRequestRequestTypeDef = TypedDict(
    "GetCompatibleVersionsRequestRequestTypeDef",
    {
        "DomainName": str,
    },
    total=False,
)

_RequiredGetPackageVersionHistoryRequestRequestTypeDef = TypedDict(
    "_RequiredGetPackageVersionHistoryRequestRequestTypeDef",
    {
        "PackageID": str,
    },
)
_OptionalGetPackageVersionHistoryRequestRequestTypeDef = TypedDict(
    "_OptionalGetPackageVersionHistoryRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

class GetPackageVersionHistoryRequestRequestTypeDef(
    _RequiredGetPackageVersionHistoryRequestRequestTypeDef,
    _OptionalGetPackageVersionHistoryRequestRequestTypeDef,
):
    pass

PackageVersionHistoryTypeDef = TypedDict(
    "PackageVersionHistoryTypeDef",
    {
        "PackageVersion": str,
        "CommitMessage": str,
        "CreatedAt": datetime,
    },
    total=False,
)

_RequiredGetUpgradeHistoryRequestRequestTypeDef = TypedDict(
    "_RequiredGetUpgradeHistoryRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalGetUpgradeHistoryRequestRequestTypeDef = TypedDict(
    "_OptionalGetUpgradeHistoryRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

class GetUpgradeHistoryRequestRequestTypeDef(
    _RequiredGetUpgradeHistoryRequestRequestTypeDef, _OptionalGetUpgradeHistoryRequestRequestTypeDef
):
    pass

GetUpgradeStatusRequestRequestTypeDef = TypedDict(
    "GetUpgradeStatusRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)

GetUpgradeStatusResponseTypeDef = TypedDict(
    "GetUpgradeStatusResponseTypeDef",
    {
        "UpgradeStep": UpgradeStepType,
        "StepStatus": UpgradeStatusType,
        "UpgradeName": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

InboundConnectionStatusTypeDef = TypedDict(
    "InboundConnectionStatusTypeDef",
    {
        "StatusCode": InboundConnectionStatusCodeType,
        "Message": str,
    },
    total=False,
)

InstanceCountLimitsTypeDef = TypedDict(
    "InstanceCountLimitsTypeDef",
    {
        "MinimumInstanceCount": int,
        "MaximumInstanceCount": int,
    },
    total=False,
)

InstanceTypeDetailsTypeDef = TypedDict(
    "InstanceTypeDetailsTypeDef",
    {
        "InstanceType": OpenSearchPartitionInstanceTypeType,
        "EncryptionEnabled": bool,
        "CognitoEnabled": bool,
        "AppLogsEnabled": bool,
        "AdvancedSecurityEnabled": bool,
        "WarmEnabled": bool,
        "InstanceRole": List[str],
        "AvailabilityZones": List[str],
    },
    total=False,
)

ListDomainNamesRequestRequestTypeDef = TypedDict(
    "ListDomainNamesRequestRequestTypeDef",
    {
        "EngineType": EngineTypeType,
    },
    total=False,
)

_RequiredListDomainsForPackageRequestRequestTypeDef = TypedDict(
    "_RequiredListDomainsForPackageRequestRequestTypeDef",
    {
        "PackageID": str,
    },
)
_OptionalListDomainsForPackageRequestRequestTypeDef = TypedDict(
    "_OptionalListDomainsForPackageRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

class ListDomainsForPackageRequestRequestTypeDef(
    _RequiredListDomainsForPackageRequestRequestTypeDef,
    _OptionalListDomainsForPackageRequestRequestTypeDef,
):
    pass

_RequiredListInstanceTypeDetailsRequestRequestTypeDef = TypedDict(
    "_RequiredListInstanceTypeDetailsRequestRequestTypeDef",
    {
        "EngineVersion": str,
    },
)
_OptionalListInstanceTypeDetailsRequestRequestTypeDef = TypedDict(
    "_OptionalListInstanceTypeDetailsRequestRequestTypeDef",
    {
        "DomainName": str,
        "MaxResults": int,
        "NextToken": str,
        "RetrieveAZs": bool,
        "InstanceType": str,
    },
    total=False,
)

class ListInstanceTypeDetailsRequestRequestTypeDef(
    _RequiredListInstanceTypeDetailsRequestRequestTypeDef,
    _OptionalListInstanceTypeDetailsRequestRequestTypeDef,
):
    pass

_RequiredListPackagesForDomainRequestRequestTypeDef = TypedDict(
    "_RequiredListPackagesForDomainRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalListPackagesForDomainRequestRequestTypeDef = TypedDict(
    "_OptionalListPackagesForDomainRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

class ListPackagesForDomainRequestRequestTypeDef(
    _RequiredListPackagesForDomainRequestRequestTypeDef,
    _OptionalListPackagesForDomainRequestRequestTypeDef,
):
    pass

_RequiredListScheduledActionsRequestRequestTypeDef = TypedDict(
    "_RequiredListScheduledActionsRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalListScheduledActionsRequestRequestTypeDef = TypedDict(
    "_OptionalListScheduledActionsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

class ListScheduledActionsRequestRequestTypeDef(
    _RequiredListScheduledActionsRequestRequestTypeDef,
    _OptionalListScheduledActionsRequestRequestTypeDef,
):
    pass

_RequiredScheduledActionTypeDef = TypedDict(
    "_RequiredScheduledActionTypeDef",
    {
        "Id": str,
        "Type": ActionTypeType,
        "Severity": ActionSeverityType,
        "ScheduledTime": int,
    },
)
_OptionalScheduledActionTypeDef = TypedDict(
    "_OptionalScheduledActionTypeDef",
    {
        "Description": str,
        "ScheduledBy": ScheduledByType,
        "Status": ActionStatusType,
        "Mandatory": bool,
        "Cancellable": bool,
    },
    total=False,
)

class ScheduledActionTypeDef(_RequiredScheduledActionTypeDef, _OptionalScheduledActionTypeDef):
    pass

ListTagsRequestRequestTypeDef = TypedDict(
    "ListTagsRequestRequestTypeDef",
    {
        "ARN": str,
    },
)

ListVersionsRequestRequestTypeDef = TypedDict(
    "ListVersionsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListVersionsResponseTypeDef = TypedDict(
    "ListVersionsResponseTypeDef",
    {
        "Versions": List[str],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListVpcEndpointAccessRequestRequestTypeDef = TypedDict(
    "_RequiredListVpcEndpointAccessRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalListVpcEndpointAccessRequestRequestTypeDef = TypedDict(
    "_OptionalListVpcEndpointAccessRequestRequestTypeDef",
    {
        "NextToken": str,
    },
    total=False,
)

class ListVpcEndpointAccessRequestRequestTypeDef(
    _RequiredListVpcEndpointAccessRequestRequestTypeDef,
    _OptionalListVpcEndpointAccessRequestRequestTypeDef,
):
    pass

_RequiredListVpcEndpointsForDomainRequestRequestTypeDef = TypedDict(
    "_RequiredListVpcEndpointsForDomainRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalListVpcEndpointsForDomainRequestRequestTypeDef = TypedDict(
    "_OptionalListVpcEndpointsForDomainRequestRequestTypeDef",
    {
        "NextToken": str,
    },
    total=False,
)

class ListVpcEndpointsForDomainRequestRequestTypeDef(
    _RequiredListVpcEndpointsForDomainRequestRequestTypeDef,
    _OptionalListVpcEndpointsForDomainRequestRequestTypeDef,
):
    pass

ListVpcEndpointsRequestRequestTypeDef = TypedDict(
    "ListVpcEndpointsRequestRequestTypeDef",
    {
        "NextToken": str,
    },
    total=False,
)

WindowStartTimeTypeDef = TypedDict(
    "WindowStartTimeTypeDef",
    {
        "Hours": int,
        "Minutes": int,
    },
)

_RequiredPurchaseReservedInstanceOfferingRequestRequestTypeDef = TypedDict(
    "_RequiredPurchaseReservedInstanceOfferingRequestRequestTypeDef",
    {
        "ReservedInstanceOfferingId": str,
        "ReservationName": str,
    },
)
_OptionalPurchaseReservedInstanceOfferingRequestRequestTypeDef = TypedDict(
    "_OptionalPurchaseReservedInstanceOfferingRequestRequestTypeDef",
    {
        "InstanceCount": int,
    },
    total=False,
)

class PurchaseReservedInstanceOfferingRequestRequestTypeDef(
    _RequiredPurchaseReservedInstanceOfferingRequestRequestTypeDef,
    _OptionalPurchaseReservedInstanceOfferingRequestRequestTypeDef,
):
    pass

PurchaseReservedInstanceOfferingResponseTypeDef = TypedDict(
    "PurchaseReservedInstanceOfferingResponseTypeDef",
    {
        "ReservedInstanceId": str,
        "ReservationName": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

RecurringChargeTypeDef = TypedDict(
    "RecurringChargeTypeDef",
    {
        "RecurringChargeAmount": float,
        "RecurringChargeFrequency": str,
    },
    total=False,
)

RejectInboundConnectionRequestRequestTypeDef = TypedDict(
    "RejectInboundConnectionRequestRequestTypeDef",
    {
        "ConnectionId": str,
    },
)

RemoveTagsRequestRequestTypeDef = TypedDict(
    "RemoveTagsRequestRequestTypeDef",
    {
        "ARN": str,
        "TagKeys": Sequence[str],
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

RevokeVpcEndpointAccessRequestRequestTypeDef = TypedDict(
    "RevokeVpcEndpointAccessRequestRequestTypeDef",
    {
        "DomainName": str,
        "Account": str,
    },
)

SAMLIdpTypeDef = TypedDict(
    "SAMLIdpTypeDef",
    {
        "MetadataContent": str,
        "EntityId": str,
    },
)

_RequiredStartServiceSoftwareUpdateRequestRequestTypeDef = TypedDict(
    "_RequiredStartServiceSoftwareUpdateRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalStartServiceSoftwareUpdateRequestRequestTypeDef = TypedDict(
    "_OptionalStartServiceSoftwareUpdateRequestRequestTypeDef",
    {
        "ScheduleAt": ScheduleAtType,
        "DesiredStartTime": int,
    },
    total=False,
)

class StartServiceSoftwareUpdateRequestRequestTypeDef(
    _RequiredStartServiceSoftwareUpdateRequestRequestTypeDef,
    _OptionalStartServiceSoftwareUpdateRequestRequestTypeDef,
):
    pass

StorageTypeLimitTypeDef = TypedDict(
    "StorageTypeLimitTypeDef",
    {
        "LimitName": str,
        "LimitValues": List[str],
    },
    total=False,
)

_RequiredUpdateScheduledActionRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateScheduledActionRequestRequestTypeDef",
    {
        "DomainName": str,
        "ActionID": str,
        "ActionType": ActionTypeType,
        "ScheduleAt": ScheduleAtType,
    },
)
_OptionalUpdateScheduledActionRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateScheduledActionRequestRequestTypeDef",
    {
        "DesiredStartTime": int,
    },
    total=False,
)

class UpdateScheduledActionRequestRequestTypeDef(
    _RequiredUpdateScheduledActionRequestRequestTypeDef,
    _OptionalUpdateScheduledActionRequestRequestTypeDef,
):
    pass

_RequiredUpgradeDomainRequestRequestTypeDef = TypedDict(
    "_RequiredUpgradeDomainRequestRequestTypeDef",
    {
        "DomainName": str,
        "TargetVersion": str,
    },
)
_OptionalUpgradeDomainRequestRequestTypeDef = TypedDict(
    "_OptionalUpgradeDomainRequestRequestTypeDef",
    {
        "PerformCheckOnly": bool,
        "AdvancedOptions": Mapping[str, str],
    },
    total=False,
)

class UpgradeDomainRequestRequestTypeDef(
    _RequiredUpgradeDomainRequestRequestTypeDef, _OptionalUpgradeDomainRequestRequestTypeDef
):
    pass

UpgradeStepItemTypeDef = TypedDict(
    "UpgradeStepItemTypeDef",
    {
        "UpgradeStep": UpgradeStepType,
        "UpgradeStepStatus": UpgradeStatusType,
        "Issues": List[str],
        "ProgressPercent": float,
    },
    total=False,
)

DomainInformationContainerTypeDef = TypedDict(
    "DomainInformationContainerTypeDef",
    {
        "AWSDomainInformation": AWSDomainInformationTypeDef,
    },
    total=False,
)

AccessPoliciesStatusTypeDef = TypedDict(
    "AccessPoliciesStatusTypeDef",
    {
        "Options": str,
        "Status": OptionStatusTypeDef,
    },
)

AdvancedOptionsStatusTypeDef = TypedDict(
    "AdvancedOptionsStatusTypeDef",
    {
        "Options": Dict[str, str],
        "Status": OptionStatusTypeDef,
    },
)

VersionStatusTypeDef = TypedDict(
    "VersionStatusTypeDef",
    {
        "Options": str,
        "Status": OptionStatusTypeDef,
    },
)

AddTagsRequestRequestTypeDef = TypedDict(
    "AddTagsRequestRequestTypeDef",
    {
        "ARN": str,
        "TagList": Sequence[TagTypeDef],
    },
)

ListTagsResponseTypeDef = TypedDict(
    "ListTagsResponseTypeDef",
    {
        "TagList": List[TagTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

AuthorizeVpcEndpointAccessResponseTypeDef = TypedDict(
    "AuthorizeVpcEndpointAccessResponseTypeDef",
    {
        "AuthorizedPrincipal": AuthorizedPrincipalTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListVpcEndpointAccessResponseTypeDef = TypedDict(
    "ListVpcEndpointAccessResponseTypeDef",
    {
        "AuthorizedPrincipalList": List[AuthorizedPrincipalTypeDef],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

AutoTuneDetailsTypeDef = TypedDict(
    "AutoTuneDetailsTypeDef",
    {
        "ScheduledAutoTuneDetails": ScheduledAutoTuneDetailsTypeDef,
    },
    total=False,
)

AutoTuneMaintenanceScheduleTypeDef = TypedDict(
    "AutoTuneMaintenanceScheduleTypeDef",
    {
        "StartAt": Union[datetime, str],
        "Duration": DurationTypeDef,
        "CronExpressionForRecurrence": str,
    },
    total=False,
)

EnvironmentInfoTypeDef = TypedDict(
    "EnvironmentInfoTypeDef",
    {
        "AvailabilityZoneInformation": List[AvailabilityZoneInfoTypeDef],
    },
    total=False,
)

CancelServiceSoftwareUpdateResponseTypeDef = TypedDict(
    "CancelServiceSoftwareUpdateResponseTypeDef",
    {
        "ServiceSoftwareOptions": ServiceSoftwareOptionsTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

StartServiceSoftwareUpdateResponseTypeDef = TypedDict(
    "StartServiceSoftwareUpdateResponseTypeDef",
    {
        "ServiceSoftwareOptions": ServiceSoftwareOptionsTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

UpgradeDomainResponseTypeDef = TypedDict(
    "UpgradeDomainResponseTypeDef",
    {
        "UpgradeId": str,
        "DomainName": str,
        "TargetVersion": str,
        "PerformCheckOnly": bool,
        "AdvancedOptions": Dict[str, str],
        "ChangeProgressDetails": ChangeProgressDetailsTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ChangeProgressStatusDetailsTypeDef = TypedDict(
    "ChangeProgressStatusDetailsTypeDef",
    {
        "ChangeId": str,
        "StartTime": datetime,
        "Status": OverallChangeStatusType,
        "PendingProperties": List[str],
        "CompletedProperties": List[str],
        "TotalNumberOfStages": int,
        "ChangeProgressStages": List[ChangeProgressStageTypeDef],
    },
    total=False,
)

ClusterConfigTypeDef = TypedDict(
    "ClusterConfigTypeDef",
    {
        "InstanceType": OpenSearchPartitionInstanceTypeType,
        "InstanceCount": int,
        "DedicatedMasterEnabled": bool,
        "ZoneAwarenessEnabled": bool,
        "ZoneAwarenessConfig": ZoneAwarenessConfigTypeDef,
        "DedicatedMasterType": OpenSearchPartitionInstanceTypeType,
        "DedicatedMasterCount": int,
        "WarmEnabled": bool,
        "WarmType": OpenSearchWarmPartitionInstanceTypeType,
        "WarmCount": int,
        "ColdStorageOptions": ColdStorageOptionsTypeDef,
        "MultiAZWithStandbyEnabled": bool,
    },
    total=False,
)

CognitoOptionsStatusTypeDef = TypedDict(
    "CognitoOptionsStatusTypeDef",
    {
        "Options": CognitoOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
)

GetCompatibleVersionsResponseTypeDef = TypedDict(
    "GetCompatibleVersionsResponseTypeDef",
    {
        "CompatibleVersions": List[CompatibleVersionsMapTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DomainEndpointOptionsStatusTypeDef = TypedDict(
    "DomainEndpointOptionsStatusTypeDef",
    {
        "Options": DomainEndpointOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
)

EBSOptionsStatusTypeDef = TypedDict(
    "EBSOptionsStatusTypeDef",
    {
        "Options": EBSOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
)

EncryptionAtRestOptionsStatusTypeDef = TypedDict(
    "EncryptionAtRestOptionsStatusTypeDef",
    {
        "Options": EncryptionAtRestOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
)

LogPublishingOptionsStatusTypeDef = TypedDict(
    "LogPublishingOptionsStatusTypeDef",
    {
        "Options": Dict[LogTypeType, LogPublishingOptionTypeDef],
        "Status": OptionStatusTypeDef,
    },
    total=False,
)

NodeToNodeEncryptionOptionsStatusTypeDef = TypedDict(
    "NodeToNodeEncryptionOptionsStatusTypeDef",
    {
        "Options": NodeToNodeEncryptionOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
)

SnapshotOptionsStatusTypeDef = TypedDict(
    "SnapshotOptionsStatusTypeDef",
    {
        "Options": SnapshotOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
)

SoftwareUpdateOptionsStatusTypeDef = TypedDict(
    "SoftwareUpdateOptionsStatusTypeDef",
    {
        "Options": SoftwareUpdateOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
    total=False,
)

_RequiredCreateVpcEndpointRequestRequestTypeDef = TypedDict(
    "_RequiredCreateVpcEndpointRequestRequestTypeDef",
    {
        "DomainArn": str,
        "VpcOptions": VPCOptionsTypeDef,
    },
)
_OptionalCreateVpcEndpointRequestRequestTypeDef = TypedDict(
    "_OptionalCreateVpcEndpointRequestRequestTypeDef",
    {
        "ClientToken": str,
    },
    total=False,
)

class CreateVpcEndpointRequestRequestTypeDef(
    _RequiredCreateVpcEndpointRequestRequestTypeDef, _OptionalCreateVpcEndpointRequestRequestTypeDef
):
    pass

UpdateVpcEndpointRequestRequestTypeDef = TypedDict(
    "UpdateVpcEndpointRequestRequestTypeDef",
    {
        "VpcEndpointId": str,
        "VpcOptions": VPCOptionsTypeDef,
    },
)

_RequiredCreatePackageRequestRequestTypeDef = TypedDict(
    "_RequiredCreatePackageRequestRequestTypeDef",
    {
        "PackageName": str,
        "PackageType": Literal["TXT-DICTIONARY"],
        "PackageSource": PackageSourceTypeDef,
    },
)
_OptionalCreatePackageRequestRequestTypeDef = TypedDict(
    "_OptionalCreatePackageRequestRequestTypeDef",
    {
        "PackageDescription": str,
    },
    total=False,
)

class CreatePackageRequestRequestTypeDef(
    _RequiredCreatePackageRequestRequestTypeDef, _OptionalCreatePackageRequestRequestTypeDef
):
    pass

_RequiredUpdatePackageRequestRequestTypeDef = TypedDict(
    "_RequiredUpdatePackageRequestRequestTypeDef",
    {
        "PackageID": str,
        "PackageSource": PackageSourceTypeDef,
    },
)
_OptionalUpdatePackageRequestRequestTypeDef = TypedDict(
    "_OptionalUpdatePackageRequestRequestTypeDef",
    {
        "PackageDescription": str,
        "CommitMessage": str,
    },
    total=False,
)

class UpdatePackageRequestRequestTypeDef(
    _RequiredUpdatePackageRequestRequestTypeDef, _OptionalUpdatePackageRequestRequestTypeDef
):
    pass

DeleteVpcEndpointResponseTypeDef = TypedDict(
    "DeleteVpcEndpointResponseTypeDef",
    {
        "VpcEndpointSummary": VpcEndpointSummaryTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListVpcEndpointsForDomainResponseTypeDef = TypedDict(
    "ListVpcEndpointsForDomainResponseTypeDef",
    {
        "VpcEndpointSummaryList": List[VpcEndpointSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListVpcEndpointsResponseTypeDef = TypedDict(
    "ListVpcEndpointsResponseTypeDef",
    {
        "VpcEndpointSummaryList": List[VpcEndpointSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeDomainNodesResponseTypeDef = TypedDict(
    "DescribeDomainNodesResponseTypeDef",
    {
        "DomainNodesStatusList": List[DomainNodesStatusTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeInboundConnectionsRequestRequestTypeDef = TypedDict(
    "DescribeInboundConnectionsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeOutboundConnectionsRequestRequestTypeDef = TypedDict(
    "DescribeOutboundConnectionsRequestRequestTypeDef",
    {
        "Filters": Sequence[FilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribePackagesRequestRequestTypeDef = TypedDict(
    "DescribePackagesRequestRequestTypeDef",
    {
        "Filters": Sequence[DescribePackagesFilterTypeDef],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListDomainNamesResponseTypeDef = TypedDict(
    "ListDomainNamesResponseTypeDef",
    {
        "DomainNames": List[DomainInfoTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DomainPackageDetailsTypeDef = TypedDict(
    "DomainPackageDetailsTypeDef",
    {
        "PackageID": str,
        "PackageName": str,
        "PackageType": Literal["TXT-DICTIONARY"],
        "LastUpdated": datetime,
        "DomainName": str,
        "DomainPackageStatus": DomainPackageStatusType,
        "PackageVersion": str,
        "ReferencePath": str,
        "ErrorDetails": ErrorDetailsTypeDef,
    },
    total=False,
)

PackageDetailsTypeDef = TypedDict(
    "PackageDetailsTypeDef",
    {
        "PackageID": str,
        "PackageName": str,
        "PackageType": Literal["TXT-DICTIONARY"],
        "PackageDescription": str,
        "PackageStatus": PackageStatusType,
        "CreatedAt": datetime,
        "LastUpdatedAt": datetime,
        "AvailablePackageVersion": str,
        "ErrorDetails": ErrorDetailsTypeDef,
    },
    total=False,
)

VPCDerivedInfoStatusTypeDef = TypedDict(
    "VPCDerivedInfoStatusTypeDef",
    {
        "Options": VPCDerivedInfoTypeDef,
        "Status": OptionStatusTypeDef,
    },
)

VpcEndpointTypeDef = TypedDict(
    "VpcEndpointTypeDef",
    {
        "VpcEndpointId": str,
        "VpcEndpointOwner": str,
        "DomainArn": str,
        "VpcOptions": VPCDerivedInfoTypeDef,
        "Status": VpcEndpointStatusType,
        "Endpoint": str,
    },
    total=False,
)

_RequiredDryRunProgressStatusTypeDef = TypedDict(
    "_RequiredDryRunProgressStatusTypeDef",
    {
        "DryRunId": str,
        "DryRunStatus": str,
        "CreationDate": str,
        "UpdateDate": str,
    },
)
_OptionalDryRunProgressStatusTypeDef = TypedDict(
    "_OptionalDryRunProgressStatusTypeDef",
    {
        "ValidationFailures": List[ValidationFailureTypeDef],
    },
    total=False,
)

class DryRunProgressStatusTypeDef(
    _RequiredDryRunProgressStatusTypeDef, _OptionalDryRunProgressStatusTypeDef
):
    pass

GetPackageVersionHistoryResponseTypeDef = TypedDict(
    "GetPackageVersionHistoryResponseTypeDef",
    {
        "PackageID": str,
        "PackageVersionHistoryList": List[PackageVersionHistoryTypeDef],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

InstanceLimitsTypeDef = TypedDict(
    "InstanceLimitsTypeDef",
    {
        "InstanceCountLimits": InstanceCountLimitsTypeDef,
    },
    total=False,
)

ListInstanceTypeDetailsResponseTypeDef = TypedDict(
    "ListInstanceTypeDetailsResponseTypeDef",
    {
        "InstanceTypeDetails": List[InstanceTypeDetailsTypeDef],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListScheduledActionsResponseTypeDef = TypedDict(
    "ListScheduledActionsResponseTypeDef",
    {
        "ScheduledActions": List[ScheduledActionTypeDef],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

UpdateScheduledActionResponseTypeDef = TypedDict(
    "UpdateScheduledActionResponseTypeDef",
    {
        "ScheduledAction": ScheduledActionTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

OffPeakWindowTypeDef = TypedDict(
    "OffPeakWindowTypeDef",
    {
        "WindowStartTime": WindowStartTimeTypeDef,
    },
    total=False,
)

ReservedInstanceOfferingTypeDef = TypedDict(
    "ReservedInstanceOfferingTypeDef",
    {
        "ReservedInstanceOfferingId": str,
        "InstanceType": OpenSearchPartitionInstanceTypeType,
        "Duration": int,
        "FixedPrice": float,
        "UsagePrice": float,
        "CurrencyCode": str,
        "PaymentOption": ReservedInstancePaymentOptionType,
        "RecurringCharges": List[RecurringChargeTypeDef],
    },
    total=False,
)

ReservedInstanceTypeDef = TypedDict(
    "ReservedInstanceTypeDef",
    {
        "ReservationName": str,
        "ReservedInstanceId": str,
        "BillingSubscriptionId": int,
        "ReservedInstanceOfferingId": str,
        "InstanceType": OpenSearchPartitionInstanceTypeType,
        "StartTime": datetime,
        "Duration": int,
        "FixedPrice": float,
        "UsagePrice": float,
        "CurrencyCode": str,
        "InstanceCount": int,
        "State": str,
        "PaymentOption": ReservedInstancePaymentOptionType,
        "RecurringCharges": List[RecurringChargeTypeDef],
    },
    total=False,
)

SAMLOptionsInputTypeDef = TypedDict(
    "SAMLOptionsInputTypeDef",
    {
        "Enabled": bool,
        "Idp": SAMLIdpTypeDef,
        "MasterUserName": str,
        "MasterBackendRole": str,
        "SubjectKey": str,
        "RolesKey": str,
        "SessionTimeoutMinutes": int,
    },
    total=False,
)

SAMLOptionsOutputTypeDef = TypedDict(
    "SAMLOptionsOutputTypeDef",
    {
        "Enabled": bool,
        "Idp": SAMLIdpTypeDef,
        "SubjectKey": str,
        "RolesKey": str,
        "SessionTimeoutMinutes": int,
    },
    total=False,
)

StorageTypeTypeDef = TypedDict(
    "StorageTypeTypeDef",
    {
        "StorageTypeName": str,
        "StorageSubTypeName": str,
        "StorageTypeLimits": List[StorageTypeLimitTypeDef],
    },
    total=False,
)

UpgradeHistoryTypeDef = TypedDict(
    "UpgradeHistoryTypeDef",
    {
        "UpgradeName": str,
        "StartTimestamp": datetime,
        "UpgradeStatus": UpgradeStatusType,
        "StepsList": List[UpgradeStepItemTypeDef],
    },
    total=False,
)

_RequiredCreateOutboundConnectionRequestRequestTypeDef = TypedDict(
    "_RequiredCreateOutboundConnectionRequestRequestTypeDef",
    {
        "LocalDomainInfo": DomainInformationContainerTypeDef,
        "RemoteDomainInfo": DomainInformationContainerTypeDef,
        "ConnectionAlias": str,
    },
)
_OptionalCreateOutboundConnectionRequestRequestTypeDef = TypedDict(
    "_OptionalCreateOutboundConnectionRequestRequestTypeDef",
    {
        "ConnectionMode": ConnectionModeType,
    },
    total=False,
)

class CreateOutboundConnectionRequestRequestTypeDef(
    _RequiredCreateOutboundConnectionRequestRequestTypeDef,
    _OptionalCreateOutboundConnectionRequestRequestTypeDef,
):
    pass

CreateOutboundConnectionResponseTypeDef = TypedDict(
    "CreateOutboundConnectionResponseTypeDef",
    {
        "LocalDomainInfo": DomainInformationContainerTypeDef,
        "RemoteDomainInfo": DomainInformationContainerTypeDef,
        "ConnectionAlias": str,
        "ConnectionStatus": OutboundConnectionStatusTypeDef,
        "ConnectionId": str,
        "ConnectionMode": ConnectionModeType,
        "ConnectionProperties": ConnectionPropertiesTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

InboundConnectionTypeDef = TypedDict(
    "InboundConnectionTypeDef",
    {
        "LocalDomainInfo": DomainInformationContainerTypeDef,
        "RemoteDomainInfo": DomainInformationContainerTypeDef,
        "ConnectionId": str,
        "ConnectionStatus": InboundConnectionStatusTypeDef,
        "ConnectionMode": ConnectionModeType,
    },
    total=False,
)

OutboundConnectionTypeDef = TypedDict(
    "OutboundConnectionTypeDef",
    {
        "LocalDomainInfo": DomainInformationContainerTypeDef,
        "RemoteDomainInfo": DomainInformationContainerTypeDef,
        "ConnectionId": str,
        "ConnectionAlias": str,
        "ConnectionStatus": OutboundConnectionStatusTypeDef,
        "ConnectionMode": ConnectionModeType,
        "ConnectionProperties": ConnectionPropertiesTypeDef,
    },
    total=False,
)

AutoTuneTypeDef = TypedDict(
    "AutoTuneTypeDef",
    {
        "AutoTuneType": Literal["SCHEDULED_ACTION"],
        "AutoTuneDetails": AutoTuneDetailsTypeDef,
    },
    total=False,
)

AutoTuneOptionsInputTypeDef = TypedDict(
    "AutoTuneOptionsInputTypeDef",
    {
        "DesiredState": AutoTuneDesiredStateType,
        "MaintenanceSchedules": Sequence[AutoTuneMaintenanceScheduleTypeDef],
        "UseOffPeakWindow": bool,
    },
    total=False,
)

AutoTuneOptionsTypeDef = TypedDict(
    "AutoTuneOptionsTypeDef",
    {
        "DesiredState": AutoTuneDesiredStateType,
        "RollbackOnDisable": RollbackOnDisableType,
        "MaintenanceSchedules": List[AutoTuneMaintenanceScheduleTypeDef],
        "UseOffPeakWindow": bool,
    },
    total=False,
)

DescribeDomainHealthResponseTypeDef = TypedDict(
    "DescribeDomainHealthResponseTypeDef",
    {
        "DomainState": DomainStateType,
        "AvailabilityZoneCount": str,
        "ActiveAvailabilityZoneCount": str,
        "StandByAvailabilityZoneCount": str,
        "DataNodeCount": str,
        "DedicatedMaster": bool,
        "MasterEligibleNodeCount": str,
        "WarmNodeCount": str,
        "MasterNode": MasterNodeStatusType,
        "ClusterHealth": DomainHealthType,
        "TotalShards": str,
        "TotalUnAssignedShards": str,
        "EnvironmentInformation": List[EnvironmentInfoTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeDomainChangeProgressResponseTypeDef = TypedDict(
    "DescribeDomainChangeProgressResponseTypeDef",
    {
        "ChangeProgressStatus": ChangeProgressStatusDetailsTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ClusterConfigStatusTypeDef = TypedDict(
    "ClusterConfigStatusTypeDef",
    {
        "Options": ClusterConfigTypeDef,
        "Status": OptionStatusTypeDef,
    },
)

AssociatePackageResponseTypeDef = TypedDict(
    "AssociatePackageResponseTypeDef",
    {
        "DomainPackageDetails": DomainPackageDetailsTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DissociatePackageResponseTypeDef = TypedDict(
    "DissociatePackageResponseTypeDef",
    {
        "DomainPackageDetails": DomainPackageDetailsTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListDomainsForPackageResponseTypeDef = TypedDict(
    "ListDomainsForPackageResponseTypeDef",
    {
        "DomainPackageDetailsList": List[DomainPackageDetailsTypeDef],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListPackagesForDomainResponseTypeDef = TypedDict(
    "ListPackagesForDomainResponseTypeDef",
    {
        "DomainPackageDetailsList": List[DomainPackageDetailsTypeDef],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

CreatePackageResponseTypeDef = TypedDict(
    "CreatePackageResponseTypeDef",
    {
        "PackageDetails": PackageDetailsTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeletePackageResponseTypeDef = TypedDict(
    "DeletePackageResponseTypeDef",
    {
        "PackageDetails": PackageDetailsTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribePackagesResponseTypeDef = TypedDict(
    "DescribePackagesResponseTypeDef",
    {
        "PackageDetailsList": List[PackageDetailsTypeDef],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

UpdatePackageResponseTypeDef = TypedDict(
    "UpdatePackageResponseTypeDef",
    {
        "PackageDetails": PackageDetailsTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

CreateVpcEndpointResponseTypeDef = TypedDict(
    "CreateVpcEndpointResponseTypeDef",
    {
        "VpcEndpoint": VpcEndpointTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeVpcEndpointsResponseTypeDef = TypedDict(
    "DescribeVpcEndpointsResponseTypeDef",
    {
        "VpcEndpoints": List[VpcEndpointTypeDef],
        "VpcEndpointErrors": List[VpcEndpointErrorTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

UpdateVpcEndpointResponseTypeDef = TypedDict(
    "UpdateVpcEndpointResponseTypeDef",
    {
        "VpcEndpoint": VpcEndpointTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

OffPeakWindowOptionsTypeDef = TypedDict(
    "OffPeakWindowOptionsTypeDef",
    {
        "Enabled": bool,
        "OffPeakWindow": OffPeakWindowTypeDef,
    },
    total=False,
)

DescribeReservedInstanceOfferingsResponseTypeDef = TypedDict(
    "DescribeReservedInstanceOfferingsResponseTypeDef",
    {
        "NextToken": str,
        "ReservedInstanceOfferings": List[ReservedInstanceOfferingTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeReservedInstancesResponseTypeDef = TypedDict(
    "DescribeReservedInstancesResponseTypeDef",
    {
        "NextToken": str,
        "ReservedInstances": List[ReservedInstanceTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

AdvancedSecurityOptionsInputTypeDef = TypedDict(
    "AdvancedSecurityOptionsInputTypeDef",
    {
        "Enabled": bool,
        "InternalUserDatabaseEnabled": bool,
        "MasterUserOptions": MasterUserOptionsTypeDef,
        "SAMLOptions": SAMLOptionsInputTypeDef,
        "AnonymousAuthEnabled": bool,
    },
    total=False,
)

AdvancedSecurityOptionsTypeDef = TypedDict(
    "AdvancedSecurityOptionsTypeDef",
    {
        "Enabled": bool,
        "InternalUserDatabaseEnabled": bool,
        "SAMLOptions": SAMLOptionsOutputTypeDef,
        "AnonymousAuthDisableDate": datetime,
        "AnonymousAuthEnabled": bool,
    },
    total=False,
)

LimitsTypeDef = TypedDict(
    "LimitsTypeDef",
    {
        "StorageTypes": List[StorageTypeTypeDef],
        "InstanceLimits": InstanceLimitsTypeDef,
        "AdditionalLimits": List[AdditionalLimitTypeDef],
    },
    total=False,
)

GetUpgradeHistoryResponseTypeDef = TypedDict(
    "GetUpgradeHistoryResponseTypeDef",
    {
        "UpgradeHistories": List[UpgradeHistoryTypeDef],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

AcceptInboundConnectionResponseTypeDef = TypedDict(
    "AcceptInboundConnectionResponseTypeDef",
    {
        "Connection": InboundConnectionTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeleteInboundConnectionResponseTypeDef = TypedDict(
    "DeleteInboundConnectionResponseTypeDef",
    {
        "Connection": InboundConnectionTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeInboundConnectionsResponseTypeDef = TypedDict(
    "DescribeInboundConnectionsResponseTypeDef",
    {
        "Connections": List[InboundConnectionTypeDef],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

RejectInboundConnectionResponseTypeDef = TypedDict(
    "RejectInboundConnectionResponseTypeDef",
    {
        "Connection": InboundConnectionTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeleteOutboundConnectionResponseTypeDef = TypedDict(
    "DeleteOutboundConnectionResponseTypeDef",
    {
        "Connection": OutboundConnectionTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeOutboundConnectionsResponseTypeDef = TypedDict(
    "DescribeOutboundConnectionsResponseTypeDef",
    {
        "Connections": List[OutboundConnectionTypeDef],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeDomainAutoTunesResponseTypeDef = TypedDict(
    "DescribeDomainAutoTunesResponseTypeDef",
    {
        "AutoTunes": List[AutoTuneTypeDef],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

AutoTuneOptionsStatusTypeDef = TypedDict(
    "AutoTuneOptionsStatusTypeDef",
    {
        "Options": AutoTuneOptionsTypeDef,
        "Status": AutoTuneStatusTypeDef,
    },
    total=False,
)

OffPeakWindowOptionsStatusTypeDef = TypedDict(
    "OffPeakWindowOptionsStatusTypeDef",
    {
        "Options": OffPeakWindowOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
    total=False,
)

_RequiredCreateDomainRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDomainRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalCreateDomainRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDomainRequestRequestTypeDef",
    {
        "EngineVersion": str,
        "ClusterConfig": ClusterConfigTypeDef,
        "EBSOptions": EBSOptionsTypeDef,
        "AccessPolicies": str,
        "SnapshotOptions": SnapshotOptionsTypeDef,
        "VPCOptions": VPCOptionsTypeDef,
        "CognitoOptions": CognitoOptionsTypeDef,
        "EncryptionAtRestOptions": EncryptionAtRestOptionsTypeDef,
        "NodeToNodeEncryptionOptions": NodeToNodeEncryptionOptionsTypeDef,
        "AdvancedOptions": Mapping[str, str],
        "LogPublishingOptions": Mapping[LogTypeType, LogPublishingOptionTypeDef],
        "DomainEndpointOptions": DomainEndpointOptionsTypeDef,
        "AdvancedSecurityOptions": AdvancedSecurityOptionsInputTypeDef,
        "TagList": Sequence[TagTypeDef],
        "AutoTuneOptions": AutoTuneOptionsInputTypeDef,
        "OffPeakWindowOptions": OffPeakWindowOptionsTypeDef,
        "SoftwareUpdateOptions": SoftwareUpdateOptionsTypeDef,
    },
    total=False,
)

class CreateDomainRequestRequestTypeDef(
    _RequiredCreateDomainRequestRequestTypeDef, _OptionalCreateDomainRequestRequestTypeDef
):
    pass

_RequiredUpdateDomainConfigRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateDomainConfigRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalUpdateDomainConfigRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateDomainConfigRequestRequestTypeDef",
    {
        "ClusterConfig": ClusterConfigTypeDef,
        "EBSOptions": EBSOptionsTypeDef,
        "SnapshotOptions": SnapshotOptionsTypeDef,
        "VPCOptions": VPCOptionsTypeDef,
        "CognitoOptions": CognitoOptionsTypeDef,
        "AdvancedOptions": Mapping[str, str],
        "AccessPolicies": str,
        "LogPublishingOptions": Mapping[LogTypeType, LogPublishingOptionTypeDef],
        "EncryptionAtRestOptions": EncryptionAtRestOptionsTypeDef,
        "DomainEndpointOptions": DomainEndpointOptionsTypeDef,
        "NodeToNodeEncryptionOptions": NodeToNodeEncryptionOptionsTypeDef,
        "AdvancedSecurityOptions": AdvancedSecurityOptionsInputTypeDef,
        "AutoTuneOptions": AutoTuneOptionsTypeDef,
        "DryRun": bool,
        "DryRunMode": DryRunModeType,
        "OffPeakWindowOptions": OffPeakWindowOptionsTypeDef,
        "SoftwareUpdateOptions": SoftwareUpdateOptionsTypeDef,
    },
    total=False,
)

class UpdateDomainConfigRequestRequestTypeDef(
    _RequiredUpdateDomainConfigRequestRequestTypeDef,
    _OptionalUpdateDomainConfigRequestRequestTypeDef,
):
    pass

AdvancedSecurityOptionsStatusTypeDef = TypedDict(
    "AdvancedSecurityOptionsStatusTypeDef",
    {
        "Options": AdvancedSecurityOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
)

_RequiredDomainStatusTypeDef = TypedDict(
    "_RequiredDomainStatusTypeDef",
    {
        "DomainId": str,
        "DomainName": str,
        "ARN": str,
        "ClusterConfig": ClusterConfigTypeDef,
    },
)
_OptionalDomainStatusTypeDef = TypedDict(
    "_OptionalDomainStatusTypeDef",
    {
        "Created": bool,
        "Deleted": bool,
        "Endpoint": str,
        "Endpoints": Dict[str, str],
        "Processing": bool,
        "UpgradeProcessing": bool,
        "EngineVersion": str,
        "EBSOptions": EBSOptionsTypeDef,
        "AccessPolicies": str,
        "SnapshotOptions": SnapshotOptionsTypeDef,
        "VPCOptions": VPCDerivedInfoTypeDef,
        "CognitoOptions": CognitoOptionsTypeDef,
        "EncryptionAtRestOptions": EncryptionAtRestOptionsTypeDef,
        "NodeToNodeEncryptionOptions": NodeToNodeEncryptionOptionsTypeDef,
        "AdvancedOptions": Dict[str, str],
        "LogPublishingOptions": Dict[LogTypeType, LogPublishingOptionTypeDef],
        "ServiceSoftwareOptions": ServiceSoftwareOptionsTypeDef,
        "DomainEndpointOptions": DomainEndpointOptionsTypeDef,
        "AdvancedSecurityOptions": AdvancedSecurityOptionsTypeDef,
        "AutoTuneOptions": AutoTuneOptionsOutputTypeDef,
        "ChangeProgressDetails": ChangeProgressDetailsTypeDef,
        "OffPeakWindowOptions": OffPeakWindowOptionsTypeDef,
        "SoftwareUpdateOptions": SoftwareUpdateOptionsTypeDef,
    },
    total=False,
)

class DomainStatusTypeDef(_RequiredDomainStatusTypeDef, _OptionalDomainStatusTypeDef):
    pass

DescribeInstanceTypeLimitsResponseTypeDef = TypedDict(
    "DescribeInstanceTypeLimitsResponseTypeDef",
    {
        "LimitsByRole": Dict[str, LimitsTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DomainConfigTypeDef = TypedDict(
    "DomainConfigTypeDef",
    {
        "EngineVersion": VersionStatusTypeDef,
        "ClusterConfig": ClusterConfigStatusTypeDef,
        "EBSOptions": EBSOptionsStatusTypeDef,
        "AccessPolicies": AccessPoliciesStatusTypeDef,
        "SnapshotOptions": SnapshotOptionsStatusTypeDef,
        "VPCOptions": VPCDerivedInfoStatusTypeDef,
        "CognitoOptions": CognitoOptionsStatusTypeDef,
        "EncryptionAtRestOptions": EncryptionAtRestOptionsStatusTypeDef,
        "NodeToNodeEncryptionOptions": NodeToNodeEncryptionOptionsStatusTypeDef,
        "AdvancedOptions": AdvancedOptionsStatusTypeDef,
        "LogPublishingOptions": LogPublishingOptionsStatusTypeDef,
        "DomainEndpointOptions": DomainEndpointOptionsStatusTypeDef,
        "AdvancedSecurityOptions": AdvancedSecurityOptionsStatusTypeDef,
        "AutoTuneOptions": AutoTuneOptionsStatusTypeDef,
        "ChangeProgressDetails": ChangeProgressDetailsTypeDef,
        "OffPeakWindowOptions": OffPeakWindowOptionsStatusTypeDef,
        "SoftwareUpdateOptions": SoftwareUpdateOptionsStatusTypeDef,
    },
    total=False,
)

CreateDomainResponseTypeDef = TypedDict(
    "CreateDomainResponseTypeDef",
    {
        "DomainStatus": DomainStatusTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeleteDomainResponseTypeDef = TypedDict(
    "DeleteDomainResponseTypeDef",
    {
        "DomainStatus": DomainStatusTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeDomainResponseTypeDef = TypedDict(
    "DescribeDomainResponseTypeDef",
    {
        "DomainStatus": DomainStatusTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeDomainsResponseTypeDef = TypedDict(
    "DescribeDomainsResponseTypeDef",
    {
        "DomainStatusList": List[DomainStatusTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeDryRunProgressResponseTypeDef = TypedDict(
    "DescribeDryRunProgressResponseTypeDef",
    {
        "DryRunProgressStatus": DryRunProgressStatusTypeDef,
        "DryRunConfig": DomainStatusTypeDef,
        "DryRunResults": DryRunResultsTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeDomainConfigResponseTypeDef = TypedDict(
    "DescribeDomainConfigResponseTypeDef",
    {
        "DomainConfig": DomainConfigTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

UpdateDomainConfigResponseTypeDef = TypedDict(
    "UpdateDomainConfigResponseTypeDef",
    {
        "DomainConfig": DomainConfigTypeDef,
        "DryRunResults": DryRunResultsTypeDef,
        "DryRunProgressStatus": DryRunProgressStatusTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)
