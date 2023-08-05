"""
Type annotations for support service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_support/type_defs/)

Usage::

    ```python
    from mypy_boto3_support.type_defs import AttachmentTypeDef

    data: AttachmentTypeDef = {...}
    ```
"""
import sys
from typing import IO, Any, Dict, List, Sequence, Union

from botocore.response import StreamingBody

if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "AttachmentTypeDef",
    "AddAttachmentsToSetResponseTypeDef",
    "AddCommunicationToCaseRequestRequestTypeDef",
    "AddCommunicationToCaseResponseTypeDef",
    "AttachmentDetailsTypeDef",
    "CategoryTypeDef",
    "DateIntervalTypeDef",
    "SupportedHourTypeDef",
    "CreateCaseRequestRequestTypeDef",
    "CreateCaseResponseTypeDef",
    "DescribeAttachmentRequestRequestTypeDef",
    "DescribeCasesRequestDescribeCasesPaginateTypeDef",
    "DescribeCasesRequestRequestTypeDef",
    "DescribeCommunicationsRequestDescribeCommunicationsPaginateTypeDef",
    "DescribeCommunicationsRequestRequestTypeDef",
    "DescribeCreateCaseOptionsRequestRequestTypeDef",
    "DescribeServicesRequestRequestTypeDef",
    "DescribeSeverityLevelsRequestRequestTypeDef",
    "SeverityLevelTypeDef",
    "DescribeSupportedLanguagesRequestRequestTypeDef",
    "SupportedLanguageTypeDef",
    "DescribeTrustedAdvisorCheckRefreshStatusesRequestRequestTypeDef",
    "TrustedAdvisorCheckRefreshStatusTypeDef",
    "DescribeTrustedAdvisorCheckResultRequestRequestTypeDef",
    "DescribeTrustedAdvisorCheckSummariesRequestRequestTypeDef",
    "DescribeTrustedAdvisorChecksRequestRequestTypeDef",
    "TrustedAdvisorCheckDescriptionTypeDef",
    "PaginatorConfigTypeDef",
    "RefreshTrustedAdvisorCheckRequestRequestTypeDef",
    "ResolveCaseRequestRequestTypeDef",
    "ResolveCaseResponseTypeDef",
    "ResponseMetadataTypeDef",
    "TrustedAdvisorCostOptimizingSummaryTypeDef",
    "TrustedAdvisorResourceDetailTypeDef",
    "TrustedAdvisorResourcesSummaryTypeDef",
    "AddAttachmentsToSetRequestRequestTypeDef",
    "DescribeAttachmentResponseTypeDef",
    "CommunicationTypeDef",
    "ServiceTypeDef",
    "CommunicationTypeOptionsTypeDef",
    "DescribeSeverityLevelsResponseTypeDef",
    "DescribeSupportedLanguagesResponseTypeDef",
    "DescribeTrustedAdvisorCheckRefreshStatusesResponseTypeDef",
    "RefreshTrustedAdvisorCheckResponseTypeDef",
    "DescribeTrustedAdvisorChecksResponseTypeDef",
    "TrustedAdvisorCategorySpecificSummaryTypeDef",
    "DescribeCommunicationsResponseTypeDef",
    "RecentCaseCommunicationsTypeDef",
    "DescribeServicesResponseTypeDef",
    "DescribeCreateCaseOptionsResponseTypeDef",
    "TrustedAdvisorCheckResultTypeDef",
    "TrustedAdvisorCheckSummaryTypeDef",
    "CaseDetailsTypeDef",
    "DescribeTrustedAdvisorCheckResultResponseTypeDef",
    "DescribeTrustedAdvisorCheckSummariesResponseTypeDef",
    "DescribeCasesResponseTypeDef",
)

AttachmentTypeDef = TypedDict(
    "AttachmentTypeDef",
    {
        "fileName": str,
        "data": Union[str, bytes, IO[Any], StreamingBody],
    },
    total=False,
)

AddAttachmentsToSetResponseTypeDef = TypedDict(
    "AddAttachmentsToSetResponseTypeDef",
    {
        "attachmentSetId": str,
        "expiryTime": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredAddCommunicationToCaseRequestRequestTypeDef = TypedDict(
    "_RequiredAddCommunicationToCaseRequestRequestTypeDef",
    {
        "communicationBody": str,
    },
)
_OptionalAddCommunicationToCaseRequestRequestTypeDef = TypedDict(
    "_OptionalAddCommunicationToCaseRequestRequestTypeDef",
    {
        "caseId": str,
        "ccEmailAddresses": Sequence[str],
        "attachmentSetId": str,
    },
    total=False,
)


class AddCommunicationToCaseRequestRequestTypeDef(
    _RequiredAddCommunicationToCaseRequestRequestTypeDef,
    _OptionalAddCommunicationToCaseRequestRequestTypeDef,
):
    pass


AddCommunicationToCaseResponseTypeDef = TypedDict(
    "AddCommunicationToCaseResponseTypeDef",
    {
        "result": bool,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

AttachmentDetailsTypeDef = TypedDict(
    "AttachmentDetailsTypeDef",
    {
        "attachmentId": str,
        "fileName": str,
    },
    total=False,
)

CategoryTypeDef = TypedDict(
    "CategoryTypeDef",
    {
        "code": str,
        "name": str,
    },
    total=False,
)

DateIntervalTypeDef = TypedDict(
    "DateIntervalTypeDef",
    {
        "startDateTime": str,
        "endDateTime": str,
    },
    total=False,
)

SupportedHourTypeDef = TypedDict(
    "SupportedHourTypeDef",
    {
        "startTime": str,
        "endTime": str,
    },
    total=False,
)

_RequiredCreateCaseRequestRequestTypeDef = TypedDict(
    "_RequiredCreateCaseRequestRequestTypeDef",
    {
        "subject": str,
        "communicationBody": str,
    },
)
_OptionalCreateCaseRequestRequestTypeDef = TypedDict(
    "_OptionalCreateCaseRequestRequestTypeDef",
    {
        "serviceCode": str,
        "severityCode": str,
        "categoryCode": str,
        "ccEmailAddresses": Sequence[str],
        "language": str,
        "issueType": str,
        "attachmentSetId": str,
    },
    total=False,
)


class CreateCaseRequestRequestTypeDef(
    _RequiredCreateCaseRequestRequestTypeDef, _OptionalCreateCaseRequestRequestTypeDef
):
    pass


CreateCaseResponseTypeDef = TypedDict(
    "CreateCaseResponseTypeDef",
    {
        "caseId": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeAttachmentRequestRequestTypeDef = TypedDict(
    "DescribeAttachmentRequestRequestTypeDef",
    {
        "attachmentId": str,
    },
)

DescribeCasesRequestDescribeCasesPaginateTypeDef = TypedDict(
    "DescribeCasesRequestDescribeCasesPaginateTypeDef",
    {
        "caseIdList": Sequence[str],
        "displayId": str,
        "afterTime": str,
        "beforeTime": str,
        "includeResolvedCases": bool,
        "language": str,
        "includeCommunications": bool,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

DescribeCasesRequestRequestTypeDef = TypedDict(
    "DescribeCasesRequestRequestTypeDef",
    {
        "caseIdList": Sequence[str],
        "displayId": str,
        "afterTime": str,
        "beforeTime": str,
        "includeResolvedCases": bool,
        "nextToken": str,
        "maxResults": int,
        "language": str,
        "includeCommunications": bool,
    },
    total=False,
)

_RequiredDescribeCommunicationsRequestDescribeCommunicationsPaginateTypeDef = TypedDict(
    "_RequiredDescribeCommunicationsRequestDescribeCommunicationsPaginateTypeDef",
    {
        "caseId": str,
    },
)
_OptionalDescribeCommunicationsRequestDescribeCommunicationsPaginateTypeDef = TypedDict(
    "_OptionalDescribeCommunicationsRequestDescribeCommunicationsPaginateTypeDef",
    {
        "beforeTime": str,
        "afterTime": str,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)


class DescribeCommunicationsRequestDescribeCommunicationsPaginateTypeDef(
    _RequiredDescribeCommunicationsRequestDescribeCommunicationsPaginateTypeDef,
    _OptionalDescribeCommunicationsRequestDescribeCommunicationsPaginateTypeDef,
):
    pass


_RequiredDescribeCommunicationsRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeCommunicationsRequestRequestTypeDef",
    {
        "caseId": str,
    },
)
_OptionalDescribeCommunicationsRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeCommunicationsRequestRequestTypeDef",
    {
        "beforeTime": str,
        "afterTime": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)


class DescribeCommunicationsRequestRequestTypeDef(
    _RequiredDescribeCommunicationsRequestRequestTypeDef,
    _OptionalDescribeCommunicationsRequestRequestTypeDef,
):
    pass


DescribeCreateCaseOptionsRequestRequestTypeDef = TypedDict(
    "DescribeCreateCaseOptionsRequestRequestTypeDef",
    {
        "issueType": str,
        "serviceCode": str,
        "language": str,
        "categoryCode": str,
    },
)

DescribeServicesRequestRequestTypeDef = TypedDict(
    "DescribeServicesRequestRequestTypeDef",
    {
        "serviceCodeList": Sequence[str],
        "language": str,
    },
    total=False,
)

DescribeSeverityLevelsRequestRequestTypeDef = TypedDict(
    "DescribeSeverityLevelsRequestRequestTypeDef",
    {
        "language": str,
    },
    total=False,
)

SeverityLevelTypeDef = TypedDict(
    "SeverityLevelTypeDef",
    {
        "code": str,
        "name": str,
    },
    total=False,
)

DescribeSupportedLanguagesRequestRequestTypeDef = TypedDict(
    "DescribeSupportedLanguagesRequestRequestTypeDef",
    {
        "issueType": str,
        "serviceCode": str,
        "categoryCode": str,
    },
)

SupportedLanguageTypeDef = TypedDict(
    "SupportedLanguageTypeDef",
    {
        "code": str,
        "language": str,
        "display": str,
    },
    total=False,
)

DescribeTrustedAdvisorCheckRefreshStatusesRequestRequestTypeDef = TypedDict(
    "DescribeTrustedAdvisorCheckRefreshStatusesRequestRequestTypeDef",
    {
        "checkIds": Sequence[str],
    },
)

TrustedAdvisorCheckRefreshStatusTypeDef = TypedDict(
    "TrustedAdvisorCheckRefreshStatusTypeDef",
    {
        "checkId": str,
        "status": str,
        "millisUntilNextRefreshable": int,
    },
)

_RequiredDescribeTrustedAdvisorCheckResultRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeTrustedAdvisorCheckResultRequestRequestTypeDef",
    {
        "checkId": str,
    },
)
_OptionalDescribeTrustedAdvisorCheckResultRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeTrustedAdvisorCheckResultRequestRequestTypeDef",
    {
        "language": str,
    },
    total=False,
)


class DescribeTrustedAdvisorCheckResultRequestRequestTypeDef(
    _RequiredDescribeTrustedAdvisorCheckResultRequestRequestTypeDef,
    _OptionalDescribeTrustedAdvisorCheckResultRequestRequestTypeDef,
):
    pass


DescribeTrustedAdvisorCheckSummariesRequestRequestTypeDef = TypedDict(
    "DescribeTrustedAdvisorCheckSummariesRequestRequestTypeDef",
    {
        "checkIds": Sequence[str],
    },
)

DescribeTrustedAdvisorChecksRequestRequestTypeDef = TypedDict(
    "DescribeTrustedAdvisorChecksRequestRequestTypeDef",
    {
        "language": str,
    },
)

TrustedAdvisorCheckDescriptionTypeDef = TypedDict(
    "TrustedAdvisorCheckDescriptionTypeDef",
    {
        "id": str,
        "name": str,
        "description": str,
        "category": str,
        "metadata": List[str],
    },
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

RefreshTrustedAdvisorCheckRequestRequestTypeDef = TypedDict(
    "RefreshTrustedAdvisorCheckRequestRequestTypeDef",
    {
        "checkId": str,
    },
)

ResolveCaseRequestRequestTypeDef = TypedDict(
    "ResolveCaseRequestRequestTypeDef",
    {
        "caseId": str,
    },
    total=False,
)

ResolveCaseResponseTypeDef = TypedDict(
    "ResolveCaseResponseTypeDef",
    {
        "initialCaseStatus": str,
        "finalCaseStatus": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
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

TrustedAdvisorCostOptimizingSummaryTypeDef = TypedDict(
    "TrustedAdvisorCostOptimizingSummaryTypeDef",
    {
        "estimatedMonthlySavings": float,
        "estimatedPercentMonthlySavings": float,
    },
)

_RequiredTrustedAdvisorResourceDetailTypeDef = TypedDict(
    "_RequiredTrustedAdvisorResourceDetailTypeDef",
    {
        "status": str,
        "resourceId": str,
        "metadata": List[str],
    },
)
_OptionalTrustedAdvisorResourceDetailTypeDef = TypedDict(
    "_OptionalTrustedAdvisorResourceDetailTypeDef",
    {
        "region": str,
        "isSuppressed": bool,
    },
    total=False,
)


class TrustedAdvisorResourceDetailTypeDef(
    _RequiredTrustedAdvisorResourceDetailTypeDef, _OptionalTrustedAdvisorResourceDetailTypeDef
):
    pass


TrustedAdvisorResourcesSummaryTypeDef = TypedDict(
    "TrustedAdvisorResourcesSummaryTypeDef",
    {
        "resourcesProcessed": int,
        "resourcesFlagged": int,
        "resourcesIgnored": int,
        "resourcesSuppressed": int,
    },
)

_RequiredAddAttachmentsToSetRequestRequestTypeDef = TypedDict(
    "_RequiredAddAttachmentsToSetRequestRequestTypeDef",
    {
        "attachments": Sequence[AttachmentTypeDef],
    },
)
_OptionalAddAttachmentsToSetRequestRequestTypeDef = TypedDict(
    "_OptionalAddAttachmentsToSetRequestRequestTypeDef",
    {
        "attachmentSetId": str,
    },
    total=False,
)


class AddAttachmentsToSetRequestRequestTypeDef(
    _RequiredAddAttachmentsToSetRequestRequestTypeDef,
    _OptionalAddAttachmentsToSetRequestRequestTypeDef,
):
    pass


DescribeAttachmentResponseTypeDef = TypedDict(
    "DescribeAttachmentResponseTypeDef",
    {
        "attachment": AttachmentTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

CommunicationTypeDef = TypedDict(
    "CommunicationTypeDef",
    {
        "caseId": str,
        "body": str,
        "submittedBy": str,
        "timeCreated": str,
        "attachmentSet": List[AttachmentDetailsTypeDef],
    },
    total=False,
)

ServiceTypeDef = TypedDict(
    "ServiceTypeDef",
    {
        "code": str,
        "name": str,
        "categories": List[CategoryTypeDef],
    },
    total=False,
)

CommunicationTypeOptionsTypeDef = TypedDict(
    "CommunicationTypeOptionsTypeDef",
    {
        "type": str,
        "supportedHours": List[SupportedHourTypeDef],
        "datesWithoutSupport": List[DateIntervalTypeDef],
    },
    total=False,
)

DescribeSeverityLevelsResponseTypeDef = TypedDict(
    "DescribeSeverityLevelsResponseTypeDef",
    {
        "severityLevels": List[SeverityLevelTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeSupportedLanguagesResponseTypeDef = TypedDict(
    "DescribeSupportedLanguagesResponseTypeDef",
    {
        "supportedLanguages": List[SupportedLanguageTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeTrustedAdvisorCheckRefreshStatusesResponseTypeDef = TypedDict(
    "DescribeTrustedAdvisorCheckRefreshStatusesResponseTypeDef",
    {
        "statuses": List[TrustedAdvisorCheckRefreshStatusTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

RefreshTrustedAdvisorCheckResponseTypeDef = TypedDict(
    "RefreshTrustedAdvisorCheckResponseTypeDef",
    {
        "status": TrustedAdvisorCheckRefreshStatusTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeTrustedAdvisorChecksResponseTypeDef = TypedDict(
    "DescribeTrustedAdvisorChecksResponseTypeDef",
    {
        "checks": List[TrustedAdvisorCheckDescriptionTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

TrustedAdvisorCategorySpecificSummaryTypeDef = TypedDict(
    "TrustedAdvisorCategorySpecificSummaryTypeDef",
    {
        "costOptimizing": TrustedAdvisorCostOptimizingSummaryTypeDef,
    },
    total=False,
)

DescribeCommunicationsResponseTypeDef = TypedDict(
    "DescribeCommunicationsResponseTypeDef",
    {
        "communications": List[CommunicationTypeDef],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

RecentCaseCommunicationsTypeDef = TypedDict(
    "RecentCaseCommunicationsTypeDef",
    {
        "communications": List[CommunicationTypeDef],
        "nextToken": str,
    },
    total=False,
)

DescribeServicesResponseTypeDef = TypedDict(
    "DescribeServicesResponseTypeDef",
    {
        "services": List[ServiceTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeCreateCaseOptionsResponseTypeDef = TypedDict(
    "DescribeCreateCaseOptionsResponseTypeDef",
    {
        "languageAvailability": str,
        "communicationTypes": List[CommunicationTypeOptionsTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

TrustedAdvisorCheckResultTypeDef = TypedDict(
    "TrustedAdvisorCheckResultTypeDef",
    {
        "checkId": str,
        "timestamp": str,
        "status": str,
        "resourcesSummary": TrustedAdvisorResourcesSummaryTypeDef,
        "categorySpecificSummary": TrustedAdvisorCategorySpecificSummaryTypeDef,
        "flaggedResources": List[TrustedAdvisorResourceDetailTypeDef],
    },
)

_RequiredTrustedAdvisorCheckSummaryTypeDef = TypedDict(
    "_RequiredTrustedAdvisorCheckSummaryTypeDef",
    {
        "checkId": str,
        "timestamp": str,
        "status": str,
        "resourcesSummary": TrustedAdvisorResourcesSummaryTypeDef,
        "categorySpecificSummary": TrustedAdvisorCategorySpecificSummaryTypeDef,
    },
)
_OptionalTrustedAdvisorCheckSummaryTypeDef = TypedDict(
    "_OptionalTrustedAdvisorCheckSummaryTypeDef",
    {
        "hasFlaggedResources": bool,
    },
    total=False,
)


class TrustedAdvisorCheckSummaryTypeDef(
    _RequiredTrustedAdvisorCheckSummaryTypeDef, _OptionalTrustedAdvisorCheckSummaryTypeDef
):
    pass


CaseDetailsTypeDef = TypedDict(
    "CaseDetailsTypeDef",
    {
        "caseId": str,
        "displayId": str,
        "subject": str,
        "status": str,
        "serviceCode": str,
        "categoryCode": str,
        "severityCode": str,
        "submittedBy": str,
        "timeCreated": str,
        "recentCommunications": RecentCaseCommunicationsTypeDef,
        "ccEmailAddresses": List[str],
        "language": str,
    },
    total=False,
)

DescribeTrustedAdvisorCheckResultResponseTypeDef = TypedDict(
    "DescribeTrustedAdvisorCheckResultResponseTypeDef",
    {
        "result": TrustedAdvisorCheckResultTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeTrustedAdvisorCheckSummariesResponseTypeDef = TypedDict(
    "DescribeTrustedAdvisorCheckSummariesResponseTypeDef",
    {
        "summaries": List[TrustedAdvisorCheckSummaryTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeCasesResponseTypeDef = TypedDict(
    "DescribeCasesResponseTypeDef",
    {
        "cases": List[CaseDetailsTypeDef],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)
