"""
Type annotations for omics service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/type_defs/)

Usage::

    ```python
    from mypy_boto3_omics.type_defs import AbortMultipartReadSetUploadRequestRequestTypeDef

    data: AbortMultipartReadSetUploadRequestRequestTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import IO, Any, Dict, List, Mapping, Sequence, Union

from botocore.response import StreamingBody

from .literals import (
    AnnotationTypeType,
    FileTypeType,
    FormatToHeaderKeyType,
    JobStatusType,
    ReadSetActivationJobItemStatusType,
    ReadSetActivationJobStatusType,
    ReadSetExportJobItemStatusType,
    ReadSetExportJobStatusType,
    ReadSetFileType,
    ReadSetImportJobItemStatusType,
    ReadSetImportJobStatusType,
    ReadSetPartSourceType,
    ReadSetStatusType,
    ReferenceFileType,
    ReferenceImportJobItemStatusType,
    ReferenceImportJobStatusType,
    ReferenceStatusType,
    RunLogLevelType,
    RunStatusType,
    SchemaValueTypeType,
    StoreFormatType,
    StoreStatusType,
    TaskStatusType,
    WorkflowEngineType,
    WorkflowStatusType,
    WorkflowTypeType,
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
    "AbortMultipartReadSetUploadRequestRequestTypeDef",
    "ActivateReadSetFilterTypeDef",
    "ActivateReadSetJobItemTypeDef",
    "ActivateReadSetSourceItemTypeDef",
    "AnnotationImportItemDetailTypeDef",
    "AnnotationImportItemSourceTypeDef",
    "AnnotationImportJobItemTypeDef",
    "ReferenceItemTypeDef",
    "SseConfigTypeDef",
    "BatchDeleteReadSetRequestRequestTypeDef",
    "ReadSetBatchErrorTypeDef",
    "CancelAnnotationImportRequestRequestTypeDef",
    "CancelRunRequestRequestTypeDef",
    "CancelVariantImportRequestRequestTypeDef",
    "CompleteReadSetUploadPartListItemTypeDef",
    "CompleteMultipartReadSetUploadResponseTypeDef",
    "CreateMultipartReadSetUploadRequestRequestTypeDef",
    "CreateMultipartReadSetUploadResponseTypeDef",
    "CreateRunGroupRequestRequestTypeDef",
    "CreateRunGroupResponseTypeDef",
    "WorkflowParameterTypeDef",
    "CreateWorkflowResponseTypeDef",
    "DeleteAnnotationStoreRequestRequestTypeDef",
    "DeleteAnnotationStoreResponseTypeDef",
    "DeleteReferenceRequestRequestTypeDef",
    "DeleteReferenceStoreRequestRequestTypeDef",
    "DeleteRunGroupRequestRequestTypeDef",
    "DeleteRunRequestRequestTypeDef",
    "DeleteSequenceStoreRequestRequestTypeDef",
    "DeleteVariantStoreRequestRequestTypeDef",
    "DeleteVariantStoreResponseTypeDef",
    "DeleteWorkflowRequestRequestTypeDef",
    "EmptyResponseMetadataTypeDef",
    "ExportReadSetDetailTypeDef",
    "ExportReadSetFilterTypeDef",
    "ExportReadSetJobDetailTypeDef",
    "ExportReadSetTypeDef",
    "FileInformationTypeDef",
    "VcfOptionsTypeDef",
    "WaiterConfigTypeDef",
    "GetAnnotationImportRequestRequestTypeDef",
    "GetAnnotationStoreRequestRequestTypeDef",
    "GetReadSetActivationJobRequestRequestTypeDef",
    "GetReadSetExportJobRequestRequestTypeDef",
    "GetReadSetImportJobRequestRequestTypeDef",
    "GetReadSetMetadataRequestRequestTypeDef",
    "SequenceInformationTypeDef",
    "GetReadSetRequestRequestTypeDef",
    "GetReadSetResponseTypeDef",
    "GetReferenceImportJobRequestRequestTypeDef",
    "ImportReferenceSourceItemTypeDef",
    "GetReferenceMetadataRequestRequestTypeDef",
    "GetReferenceRequestRequestTypeDef",
    "GetReferenceResponseTypeDef",
    "GetReferenceStoreRequestRequestTypeDef",
    "GetRunGroupRequestRequestTypeDef",
    "GetRunGroupResponseTypeDef",
    "GetRunRequestRequestTypeDef",
    "GetRunResponseTypeDef",
    "GetRunTaskRequestRequestTypeDef",
    "GetRunTaskResponseTypeDef",
    "GetSequenceStoreRequestRequestTypeDef",
    "GetVariantImportRequestRequestTypeDef",
    "VariantImportItemDetailTypeDef",
    "GetVariantStoreRequestRequestTypeDef",
    "GetWorkflowRequestRequestTypeDef",
    "ImportReadSetFilterTypeDef",
    "ImportReadSetJobItemTypeDef",
    "SourceFilesTypeDef",
    "ImportReferenceFilterTypeDef",
    "ImportReferenceJobItemTypeDef",
    "ListAnnotationImportJobsFilterTypeDef",
    "ListAnnotationStoresFilterTypeDef",
    "ListMultipartReadSetUploadsRequestListMultipartReadSetUploadsPaginateTypeDef",
    "ListMultipartReadSetUploadsRequestRequestTypeDef",
    "MultipartReadSetUploadListItemTypeDef",
    "ReadSetUploadPartListFilterTypeDef",
    "ReadSetUploadPartListItemTypeDef",
    "ReadSetFilterTypeDef",
    "ReferenceStoreFilterTypeDef",
    "ReferenceFilterTypeDef",
    "ReferenceListItemTypeDef",
    "ListRunGroupsRequestListRunGroupsPaginateTypeDef",
    "ListRunGroupsRequestRequestTypeDef",
    "RunGroupListItemTypeDef",
    "ListRunTasksRequestListRunTasksPaginateTypeDef",
    "ListRunTasksRequestRequestTypeDef",
    "TaskListItemTypeDef",
    "ListRunsRequestListRunsPaginateTypeDef",
    "ListRunsRequestRequestTypeDef",
    "RunListItemTypeDef",
    "SequenceStoreFilterTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "ListVariantImportJobsFilterTypeDef",
    "VariantImportJobItemTypeDef",
    "ListVariantStoresFilterTypeDef",
    "ListWorkflowsRequestListWorkflowsPaginateTypeDef",
    "ListWorkflowsRequestRequestTypeDef",
    "WorkflowListItemTypeDef",
    "PaginatorConfigTypeDef",
    "ReadOptionsTypeDef",
    "ResponseMetadataTypeDef",
    "StartAnnotationImportResponseTypeDef",
    "StartReadSetActivationJobSourceItemTypeDef",
    "StartReadSetActivationJobResponseTypeDef",
    "StartReadSetExportJobResponseTypeDef",
    "StartReadSetImportJobResponseTypeDef",
    "StartReferenceImportJobSourceItemTypeDef",
    "StartReferenceImportJobResponseTypeDef",
    "StartRunRequestRequestTypeDef",
    "StartRunResponseTypeDef",
    "VariantImportItemSourceTypeDef",
    "StartVariantImportResponseTypeDef",
    "TsvStoreOptionsTypeDef",
    "TagResourceRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateAnnotationStoreRequestRequestTypeDef",
    "UpdateRunGroupRequestRequestTypeDef",
    "UpdateVariantStoreRequestRequestTypeDef",
    "UpdateWorkflowRequestRequestTypeDef",
    "UploadReadSetPartRequestRequestTypeDef",
    "UploadReadSetPartResponseTypeDef",
    "ListReadSetActivationJobsRequestListReadSetActivationJobsPaginateTypeDef",
    "ListReadSetActivationJobsRequestRequestTypeDef",
    "ListReadSetActivationJobsResponseTypeDef",
    "GetReadSetActivationJobResponseTypeDef",
    "ListAnnotationImportJobsResponseTypeDef",
    "CreateVariantStoreResponseTypeDef",
    "UpdateVariantStoreResponseTypeDef",
    "AnnotationStoreItemTypeDef",
    "CreateReferenceStoreRequestRequestTypeDef",
    "CreateReferenceStoreResponseTypeDef",
    "CreateSequenceStoreRequestRequestTypeDef",
    "CreateSequenceStoreResponseTypeDef",
    "CreateVariantStoreRequestRequestTypeDef",
    "GetReferenceStoreResponseTypeDef",
    "GetSequenceStoreResponseTypeDef",
    "GetVariantStoreResponseTypeDef",
    "ReferenceStoreDetailTypeDef",
    "SequenceStoreDetailTypeDef",
    "VariantStoreItemTypeDef",
    "BatchDeleteReadSetResponseTypeDef",
    "CompleteMultipartReadSetUploadRequestRequestTypeDef",
    "CreateWorkflowRequestRequestTypeDef",
    "GetWorkflowResponseTypeDef",
    "GetReadSetExportJobResponseTypeDef",
    "ListReadSetExportJobsRequestListReadSetExportJobsPaginateTypeDef",
    "ListReadSetExportJobsRequestRequestTypeDef",
    "ListReadSetExportJobsResponseTypeDef",
    "StartReadSetExportJobRequestRequestTypeDef",
    "ReadSetFilesTypeDef",
    "ReferenceFilesTypeDef",
    "GetAnnotationImportRequestAnnotationImportJobCreatedWaitTypeDef",
    "GetAnnotationStoreRequestAnnotationStoreCreatedWaitTypeDef",
    "GetAnnotationStoreRequestAnnotationStoreDeletedWaitTypeDef",
    "GetReadSetActivationJobRequestReadSetActivationJobCompletedWaitTypeDef",
    "GetReadSetExportJobRequestReadSetExportJobCompletedWaitTypeDef",
    "GetReadSetImportJobRequestReadSetImportJobCompletedWaitTypeDef",
    "GetReferenceImportJobRequestReferenceImportJobCompletedWaitTypeDef",
    "GetRunRequestRunCompletedWaitTypeDef",
    "GetRunRequestRunRunningWaitTypeDef",
    "GetRunTaskRequestTaskCompletedWaitTypeDef",
    "GetRunTaskRequestTaskRunningWaitTypeDef",
    "GetVariantImportRequestVariantImportJobCreatedWaitTypeDef",
    "GetVariantStoreRequestVariantStoreCreatedWaitTypeDef",
    "GetVariantStoreRequestVariantStoreDeletedWaitTypeDef",
    "GetWorkflowRequestWorkflowActiveWaitTypeDef",
    "ReadSetListItemTypeDef",
    "GetReferenceImportJobResponseTypeDef",
    "GetVariantImportResponseTypeDef",
    "ListReadSetImportJobsRequestListReadSetImportJobsPaginateTypeDef",
    "ListReadSetImportJobsRequestRequestTypeDef",
    "ListReadSetImportJobsResponseTypeDef",
    "ImportReadSetSourceItemTypeDef",
    "StartReadSetImportJobSourceItemTypeDef",
    "ListReferenceImportJobsRequestListReferenceImportJobsPaginateTypeDef",
    "ListReferenceImportJobsRequestRequestTypeDef",
    "ListReferenceImportJobsResponseTypeDef",
    "ListAnnotationImportJobsRequestListAnnotationImportJobsPaginateTypeDef",
    "ListAnnotationImportJobsRequestRequestTypeDef",
    "ListAnnotationStoresRequestListAnnotationStoresPaginateTypeDef",
    "ListAnnotationStoresRequestRequestTypeDef",
    "ListMultipartReadSetUploadsResponseTypeDef",
    "ListReadSetUploadPartsRequestListReadSetUploadPartsPaginateTypeDef",
    "ListReadSetUploadPartsRequestRequestTypeDef",
    "ListReadSetUploadPartsResponseTypeDef",
    "ListReadSetsRequestListReadSetsPaginateTypeDef",
    "ListReadSetsRequestRequestTypeDef",
    "ListReferenceStoresRequestListReferenceStoresPaginateTypeDef",
    "ListReferenceStoresRequestRequestTypeDef",
    "ListReferencesRequestListReferencesPaginateTypeDef",
    "ListReferencesRequestRequestTypeDef",
    "ListReferencesResponseTypeDef",
    "ListRunGroupsResponseTypeDef",
    "ListRunTasksResponseTypeDef",
    "ListRunsResponseTypeDef",
    "ListSequenceStoresRequestListSequenceStoresPaginateTypeDef",
    "ListSequenceStoresRequestRequestTypeDef",
    "ListVariantImportJobsRequestListVariantImportJobsPaginateTypeDef",
    "ListVariantImportJobsRequestRequestTypeDef",
    "ListVariantImportJobsResponseTypeDef",
    "ListVariantStoresRequestListVariantStoresPaginateTypeDef",
    "ListVariantStoresRequestRequestTypeDef",
    "ListWorkflowsResponseTypeDef",
    "TsvOptionsTypeDef",
    "StartReadSetActivationJobRequestRequestTypeDef",
    "StartReferenceImportJobRequestRequestTypeDef",
    "StartVariantImportRequestRequestTypeDef",
    "StoreOptionsTypeDef",
    "ListAnnotationStoresResponseTypeDef",
    "ListReferenceStoresResponseTypeDef",
    "ListSequenceStoresResponseTypeDef",
    "ListVariantStoresResponseTypeDef",
    "GetReadSetMetadataResponseTypeDef",
    "GetReferenceMetadataResponseTypeDef",
    "ListReadSetsResponseTypeDef",
    "GetReadSetImportJobResponseTypeDef",
    "StartReadSetImportJobRequestRequestTypeDef",
    "FormatOptionsTypeDef",
    "CreateAnnotationStoreRequestRequestTypeDef",
    "CreateAnnotationStoreResponseTypeDef",
    "GetAnnotationStoreResponseTypeDef",
    "UpdateAnnotationStoreResponseTypeDef",
    "GetAnnotationImportResponseTypeDef",
    "StartAnnotationImportRequestRequestTypeDef",
)

AbortMultipartReadSetUploadRequestRequestTypeDef = TypedDict(
    "AbortMultipartReadSetUploadRequestRequestTypeDef",
    {
        "sequenceStoreId": str,
        "uploadId": str,
    },
)

ActivateReadSetFilterTypeDef = TypedDict(
    "ActivateReadSetFilterTypeDef",
    {
        "status": ReadSetActivationJobStatusType,
        "createdAfter": Union[datetime, str],
        "createdBefore": Union[datetime, str],
    },
    total=False,
)

_RequiredActivateReadSetJobItemTypeDef = TypedDict(
    "_RequiredActivateReadSetJobItemTypeDef",
    {
        "id": str,
        "sequenceStoreId": str,
        "status": ReadSetActivationJobStatusType,
        "creationTime": datetime,
    },
)
_OptionalActivateReadSetJobItemTypeDef = TypedDict(
    "_OptionalActivateReadSetJobItemTypeDef",
    {
        "completionTime": datetime,
    },
    total=False,
)

class ActivateReadSetJobItemTypeDef(
    _RequiredActivateReadSetJobItemTypeDef, _OptionalActivateReadSetJobItemTypeDef
):
    pass

_RequiredActivateReadSetSourceItemTypeDef = TypedDict(
    "_RequiredActivateReadSetSourceItemTypeDef",
    {
        "readSetId": str,
        "status": ReadSetActivationJobItemStatusType,
    },
)
_OptionalActivateReadSetSourceItemTypeDef = TypedDict(
    "_OptionalActivateReadSetSourceItemTypeDef",
    {
        "statusMessage": str,
    },
    total=False,
)

class ActivateReadSetSourceItemTypeDef(
    _RequiredActivateReadSetSourceItemTypeDef, _OptionalActivateReadSetSourceItemTypeDef
):
    pass

AnnotationImportItemDetailTypeDef = TypedDict(
    "AnnotationImportItemDetailTypeDef",
    {
        "source": str,
        "jobStatus": JobStatusType,
    },
)

AnnotationImportItemSourceTypeDef = TypedDict(
    "AnnotationImportItemSourceTypeDef",
    {
        "source": str,
    },
)

_RequiredAnnotationImportJobItemTypeDef = TypedDict(
    "_RequiredAnnotationImportJobItemTypeDef",
    {
        "id": str,
        "destinationName": str,
        "roleArn": str,
        "status": JobStatusType,
        "creationTime": datetime,
        "updateTime": datetime,
    },
)
_OptionalAnnotationImportJobItemTypeDef = TypedDict(
    "_OptionalAnnotationImportJobItemTypeDef",
    {
        "completionTime": datetime,
        "runLeftNormalization": bool,
        "annotationFields": Dict[str, str],
    },
    total=False,
)

class AnnotationImportJobItemTypeDef(
    _RequiredAnnotationImportJobItemTypeDef, _OptionalAnnotationImportJobItemTypeDef
):
    pass

ReferenceItemTypeDef = TypedDict(
    "ReferenceItemTypeDef",
    {
        "referenceArn": str,
    },
    total=False,
)

_RequiredSseConfigTypeDef = TypedDict(
    "_RequiredSseConfigTypeDef",
    {
        "type": Literal["KMS"],
    },
)
_OptionalSseConfigTypeDef = TypedDict(
    "_OptionalSseConfigTypeDef",
    {
        "keyArn": str,
    },
    total=False,
)

class SseConfigTypeDef(_RequiredSseConfigTypeDef, _OptionalSseConfigTypeDef):
    pass

BatchDeleteReadSetRequestRequestTypeDef = TypedDict(
    "BatchDeleteReadSetRequestRequestTypeDef",
    {
        "ids": Sequence[str],
        "sequenceStoreId": str,
    },
)

ReadSetBatchErrorTypeDef = TypedDict(
    "ReadSetBatchErrorTypeDef",
    {
        "id": str,
        "code": str,
        "message": str,
    },
)

CancelAnnotationImportRequestRequestTypeDef = TypedDict(
    "CancelAnnotationImportRequestRequestTypeDef",
    {
        "jobId": str,
    },
)

CancelRunRequestRequestTypeDef = TypedDict(
    "CancelRunRequestRequestTypeDef",
    {
        "id": str,
    },
)

CancelVariantImportRequestRequestTypeDef = TypedDict(
    "CancelVariantImportRequestRequestTypeDef",
    {
        "jobId": str,
    },
)

CompleteReadSetUploadPartListItemTypeDef = TypedDict(
    "CompleteReadSetUploadPartListItemTypeDef",
    {
        "partNumber": int,
        "partSource": ReadSetPartSourceType,
        "checksum": str,
    },
)

CompleteMultipartReadSetUploadResponseTypeDef = TypedDict(
    "CompleteMultipartReadSetUploadResponseTypeDef",
    {
        "readSetId": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateMultipartReadSetUploadRequestRequestTypeDef = TypedDict(
    "_RequiredCreateMultipartReadSetUploadRequestRequestTypeDef",
    {
        "sequenceStoreId": str,
        "sourceFileType": FileTypeType,
        "subjectId": str,
        "sampleId": str,
        "referenceArn": str,
        "name": str,
    },
)
_OptionalCreateMultipartReadSetUploadRequestRequestTypeDef = TypedDict(
    "_OptionalCreateMultipartReadSetUploadRequestRequestTypeDef",
    {
        "clientToken": str,
        "generatedFrom": str,
        "description": str,
        "tags": Mapping[str, str],
    },
    total=False,
)

class CreateMultipartReadSetUploadRequestRequestTypeDef(
    _RequiredCreateMultipartReadSetUploadRequestRequestTypeDef,
    _OptionalCreateMultipartReadSetUploadRequestRequestTypeDef,
):
    pass

CreateMultipartReadSetUploadResponseTypeDef = TypedDict(
    "CreateMultipartReadSetUploadResponseTypeDef",
    {
        "sequenceStoreId": str,
        "uploadId": str,
        "sourceFileType": FileTypeType,
        "subjectId": str,
        "sampleId": str,
        "generatedFrom": str,
        "referenceArn": str,
        "name": str,
        "description": str,
        "tags": Dict[str, str],
        "creationTime": datetime,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateRunGroupRequestRequestTypeDef = TypedDict(
    "_RequiredCreateRunGroupRequestRequestTypeDef",
    {
        "requestId": str,
    },
)
_OptionalCreateRunGroupRequestRequestTypeDef = TypedDict(
    "_OptionalCreateRunGroupRequestRequestTypeDef",
    {
        "name": str,
        "maxCpus": int,
        "maxRuns": int,
        "maxDuration": int,
        "tags": Mapping[str, str],
        "maxGpus": int,
    },
    total=False,
)

class CreateRunGroupRequestRequestTypeDef(
    _RequiredCreateRunGroupRequestRequestTypeDef, _OptionalCreateRunGroupRequestRequestTypeDef
):
    pass

CreateRunGroupResponseTypeDef = TypedDict(
    "CreateRunGroupResponseTypeDef",
    {
        "arn": str,
        "id": str,
        "tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

WorkflowParameterTypeDef = TypedDict(
    "WorkflowParameterTypeDef",
    {
        "description": str,
        "optional": bool,
    },
    total=False,
)

CreateWorkflowResponseTypeDef = TypedDict(
    "CreateWorkflowResponseTypeDef",
    {
        "arn": str,
        "id": str,
        "status": WorkflowStatusType,
        "tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredDeleteAnnotationStoreRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteAnnotationStoreRequestRequestTypeDef",
    {
        "name": str,
    },
)
_OptionalDeleteAnnotationStoreRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteAnnotationStoreRequestRequestTypeDef",
    {
        "force": bool,
    },
    total=False,
)

class DeleteAnnotationStoreRequestRequestTypeDef(
    _RequiredDeleteAnnotationStoreRequestRequestTypeDef,
    _OptionalDeleteAnnotationStoreRequestRequestTypeDef,
):
    pass

DeleteAnnotationStoreResponseTypeDef = TypedDict(
    "DeleteAnnotationStoreResponseTypeDef",
    {
        "status": StoreStatusType,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeleteReferenceRequestRequestTypeDef = TypedDict(
    "DeleteReferenceRequestRequestTypeDef",
    {
        "id": str,
        "referenceStoreId": str,
    },
)

DeleteReferenceStoreRequestRequestTypeDef = TypedDict(
    "DeleteReferenceStoreRequestRequestTypeDef",
    {
        "id": str,
    },
)

DeleteRunGroupRequestRequestTypeDef = TypedDict(
    "DeleteRunGroupRequestRequestTypeDef",
    {
        "id": str,
    },
)

DeleteRunRequestRequestTypeDef = TypedDict(
    "DeleteRunRequestRequestTypeDef",
    {
        "id": str,
    },
)

DeleteSequenceStoreRequestRequestTypeDef = TypedDict(
    "DeleteSequenceStoreRequestRequestTypeDef",
    {
        "id": str,
    },
)

_RequiredDeleteVariantStoreRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteVariantStoreRequestRequestTypeDef",
    {
        "name": str,
    },
)
_OptionalDeleteVariantStoreRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteVariantStoreRequestRequestTypeDef",
    {
        "force": bool,
    },
    total=False,
)

class DeleteVariantStoreRequestRequestTypeDef(
    _RequiredDeleteVariantStoreRequestRequestTypeDef,
    _OptionalDeleteVariantStoreRequestRequestTypeDef,
):
    pass

DeleteVariantStoreResponseTypeDef = TypedDict(
    "DeleteVariantStoreResponseTypeDef",
    {
        "status": StoreStatusType,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeleteWorkflowRequestRequestTypeDef = TypedDict(
    "DeleteWorkflowRequestRequestTypeDef",
    {
        "id": str,
    },
)

EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredExportReadSetDetailTypeDef = TypedDict(
    "_RequiredExportReadSetDetailTypeDef",
    {
        "id": str,
        "status": ReadSetExportJobItemStatusType,
    },
)
_OptionalExportReadSetDetailTypeDef = TypedDict(
    "_OptionalExportReadSetDetailTypeDef",
    {
        "statusMessage": str,
    },
    total=False,
)

class ExportReadSetDetailTypeDef(
    _RequiredExportReadSetDetailTypeDef, _OptionalExportReadSetDetailTypeDef
):
    pass

ExportReadSetFilterTypeDef = TypedDict(
    "ExportReadSetFilterTypeDef",
    {
        "status": ReadSetExportJobStatusType,
        "createdAfter": Union[datetime, str],
        "createdBefore": Union[datetime, str],
    },
    total=False,
)

_RequiredExportReadSetJobDetailTypeDef = TypedDict(
    "_RequiredExportReadSetJobDetailTypeDef",
    {
        "id": str,
        "sequenceStoreId": str,
        "destination": str,
        "status": ReadSetExportJobStatusType,
        "creationTime": datetime,
    },
)
_OptionalExportReadSetJobDetailTypeDef = TypedDict(
    "_OptionalExportReadSetJobDetailTypeDef",
    {
        "completionTime": datetime,
    },
    total=False,
)

class ExportReadSetJobDetailTypeDef(
    _RequiredExportReadSetJobDetailTypeDef, _OptionalExportReadSetJobDetailTypeDef
):
    pass

ExportReadSetTypeDef = TypedDict(
    "ExportReadSetTypeDef",
    {
        "readSetId": str,
    },
)

FileInformationTypeDef = TypedDict(
    "FileInformationTypeDef",
    {
        "totalParts": int,
        "partSize": int,
        "contentLength": int,
    },
    total=False,
)

VcfOptionsTypeDef = TypedDict(
    "VcfOptionsTypeDef",
    {
        "ignoreQualField": bool,
        "ignoreFilterField": bool,
    },
    total=False,
)

WaiterConfigTypeDef = TypedDict(
    "WaiterConfigTypeDef",
    {
        "Delay": int,
        "MaxAttempts": int,
    },
    total=False,
)

GetAnnotationImportRequestRequestTypeDef = TypedDict(
    "GetAnnotationImportRequestRequestTypeDef",
    {
        "jobId": str,
    },
)

GetAnnotationStoreRequestRequestTypeDef = TypedDict(
    "GetAnnotationStoreRequestRequestTypeDef",
    {
        "name": str,
    },
)

GetReadSetActivationJobRequestRequestTypeDef = TypedDict(
    "GetReadSetActivationJobRequestRequestTypeDef",
    {
        "id": str,
        "sequenceStoreId": str,
    },
)

GetReadSetExportJobRequestRequestTypeDef = TypedDict(
    "GetReadSetExportJobRequestRequestTypeDef",
    {
        "sequenceStoreId": str,
        "id": str,
    },
)

GetReadSetImportJobRequestRequestTypeDef = TypedDict(
    "GetReadSetImportJobRequestRequestTypeDef",
    {
        "id": str,
        "sequenceStoreId": str,
    },
)

GetReadSetMetadataRequestRequestTypeDef = TypedDict(
    "GetReadSetMetadataRequestRequestTypeDef",
    {
        "id": str,
        "sequenceStoreId": str,
    },
)

SequenceInformationTypeDef = TypedDict(
    "SequenceInformationTypeDef",
    {
        "totalReadCount": int,
        "totalBaseCount": int,
        "generatedFrom": str,
        "alignment": str,
    },
    total=False,
)

_RequiredGetReadSetRequestRequestTypeDef = TypedDict(
    "_RequiredGetReadSetRequestRequestTypeDef",
    {
        "id": str,
        "sequenceStoreId": str,
        "partNumber": int,
    },
)
_OptionalGetReadSetRequestRequestTypeDef = TypedDict(
    "_OptionalGetReadSetRequestRequestTypeDef",
    {
        "file": ReadSetFileType,
    },
    total=False,
)

class GetReadSetRequestRequestTypeDef(
    _RequiredGetReadSetRequestRequestTypeDef, _OptionalGetReadSetRequestRequestTypeDef
):
    pass

GetReadSetResponseTypeDef = TypedDict(
    "GetReadSetResponseTypeDef",
    {
        "payload": StreamingBody,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetReferenceImportJobRequestRequestTypeDef = TypedDict(
    "GetReferenceImportJobRequestRequestTypeDef",
    {
        "id": str,
        "referenceStoreId": str,
    },
)

_RequiredImportReferenceSourceItemTypeDef = TypedDict(
    "_RequiredImportReferenceSourceItemTypeDef",
    {
        "status": ReferenceImportJobItemStatusType,
    },
)
_OptionalImportReferenceSourceItemTypeDef = TypedDict(
    "_OptionalImportReferenceSourceItemTypeDef",
    {
        "sourceFile": str,
        "statusMessage": str,
        "name": str,
        "description": str,
        "tags": Dict[str, str],
    },
    total=False,
)

class ImportReferenceSourceItemTypeDef(
    _RequiredImportReferenceSourceItemTypeDef, _OptionalImportReferenceSourceItemTypeDef
):
    pass

GetReferenceMetadataRequestRequestTypeDef = TypedDict(
    "GetReferenceMetadataRequestRequestTypeDef",
    {
        "id": str,
        "referenceStoreId": str,
    },
)

_RequiredGetReferenceRequestRequestTypeDef = TypedDict(
    "_RequiredGetReferenceRequestRequestTypeDef",
    {
        "id": str,
        "referenceStoreId": str,
        "partNumber": int,
    },
)
_OptionalGetReferenceRequestRequestTypeDef = TypedDict(
    "_OptionalGetReferenceRequestRequestTypeDef",
    {
        "range": str,
        "file": ReferenceFileType,
    },
    total=False,
)

class GetReferenceRequestRequestTypeDef(
    _RequiredGetReferenceRequestRequestTypeDef, _OptionalGetReferenceRequestRequestTypeDef
):
    pass

GetReferenceResponseTypeDef = TypedDict(
    "GetReferenceResponseTypeDef",
    {
        "payload": StreamingBody,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetReferenceStoreRequestRequestTypeDef = TypedDict(
    "GetReferenceStoreRequestRequestTypeDef",
    {
        "id": str,
    },
)

GetRunGroupRequestRequestTypeDef = TypedDict(
    "GetRunGroupRequestRequestTypeDef",
    {
        "id": str,
    },
)

GetRunGroupResponseTypeDef = TypedDict(
    "GetRunGroupResponseTypeDef",
    {
        "arn": str,
        "id": str,
        "name": str,
        "maxCpus": int,
        "maxRuns": int,
        "maxDuration": int,
        "creationTime": datetime,
        "tags": Dict[str, str],
        "maxGpus": int,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredGetRunRequestRequestTypeDef = TypedDict(
    "_RequiredGetRunRequestRequestTypeDef",
    {
        "id": str,
    },
)
_OptionalGetRunRequestRequestTypeDef = TypedDict(
    "_OptionalGetRunRequestRequestTypeDef",
    {
        "export": Sequence[Literal["DEFINITION"]],
    },
    total=False,
)

class GetRunRequestRequestTypeDef(
    _RequiredGetRunRequestRequestTypeDef, _OptionalGetRunRequestRequestTypeDef
):
    pass

GetRunResponseTypeDef = TypedDict(
    "GetRunResponseTypeDef",
    {
        "arn": str,
        "id": str,
        "status": RunStatusType,
        "workflowId": str,
        "workflowType": WorkflowTypeType,
        "runId": str,
        "roleArn": str,
        "name": str,
        "runGroupId": str,
        "priority": int,
        "definition": str,
        "digest": str,
        "parameters": Dict[str, Any],
        "storageCapacity": int,
        "outputUri": str,
        "logLevel": RunLogLevelType,
        "resourceDigests": Dict[str, str],
        "startedBy": str,
        "creationTime": datetime,
        "startTime": datetime,
        "stopTime": datetime,
        "statusMessage": str,
        "tags": Dict[str, str],
        "accelerators": Literal["GPU"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetRunTaskRequestRequestTypeDef = TypedDict(
    "GetRunTaskRequestRequestTypeDef",
    {
        "id": str,
        "taskId": str,
    },
)

GetRunTaskResponseTypeDef = TypedDict(
    "GetRunTaskResponseTypeDef",
    {
        "taskId": str,
        "status": TaskStatusType,
        "name": str,
        "cpus": int,
        "memory": int,
        "creationTime": datetime,
        "startTime": datetime,
        "stopTime": datetime,
        "statusMessage": str,
        "logStream": str,
        "gpus": int,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetSequenceStoreRequestRequestTypeDef = TypedDict(
    "GetSequenceStoreRequestRequestTypeDef",
    {
        "id": str,
    },
)

GetVariantImportRequestRequestTypeDef = TypedDict(
    "GetVariantImportRequestRequestTypeDef",
    {
        "jobId": str,
    },
)

_RequiredVariantImportItemDetailTypeDef = TypedDict(
    "_RequiredVariantImportItemDetailTypeDef",
    {
        "source": str,
        "jobStatus": JobStatusType,
    },
)
_OptionalVariantImportItemDetailTypeDef = TypedDict(
    "_OptionalVariantImportItemDetailTypeDef",
    {
        "statusMessage": str,
    },
    total=False,
)

class VariantImportItemDetailTypeDef(
    _RequiredVariantImportItemDetailTypeDef, _OptionalVariantImportItemDetailTypeDef
):
    pass

GetVariantStoreRequestRequestTypeDef = TypedDict(
    "GetVariantStoreRequestRequestTypeDef",
    {
        "name": str,
    },
)

_RequiredGetWorkflowRequestRequestTypeDef = TypedDict(
    "_RequiredGetWorkflowRequestRequestTypeDef",
    {
        "id": str,
    },
)
_OptionalGetWorkflowRequestRequestTypeDef = TypedDict(
    "_OptionalGetWorkflowRequestRequestTypeDef",
    {
        "type": WorkflowTypeType,
        "export": Sequence[Literal["DEFINITION"]],
    },
    total=False,
)

class GetWorkflowRequestRequestTypeDef(
    _RequiredGetWorkflowRequestRequestTypeDef, _OptionalGetWorkflowRequestRequestTypeDef
):
    pass

ImportReadSetFilterTypeDef = TypedDict(
    "ImportReadSetFilterTypeDef",
    {
        "status": ReadSetImportJobStatusType,
        "createdAfter": Union[datetime, str],
        "createdBefore": Union[datetime, str],
    },
    total=False,
)

_RequiredImportReadSetJobItemTypeDef = TypedDict(
    "_RequiredImportReadSetJobItemTypeDef",
    {
        "id": str,
        "sequenceStoreId": str,
        "roleArn": str,
        "status": ReadSetImportJobStatusType,
        "creationTime": datetime,
    },
)
_OptionalImportReadSetJobItemTypeDef = TypedDict(
    "_OptionalImportReadSetJobItemTypeDef",
    {
        "completionTime": datetime,
    },
    total=False,
)

class ImportReadSetJobItemTypeDef(
    _RequiredImportReadSetJobItemTypeDef, _OptionalImportReadSetJobItemTypeDef
):
    pass

_RequiredSourceFilesTypeDef = TypedDict(
    "_RequiredSourceFilesTypeDef",
    {
        "source1": str,
    },
)
_OptionalSourceFilesTypeDef = TypedDict(
    "_OptionalSourceFilesTypeDef",
    {
        "source2": str,
    },
    total=False,
)

class SourceFilesTypeDef(_RequiredSourceFilesTypeDef, _OptionalSourceFilesTypeDef):
    pass

ImportReferenceFilterTypeDef = TypedDict(
    "ImportReferenceFilterTypeDef",
    {
        "status": ReferenceImportJobStatusType,
        "createdAfter": Union[datetime, str],
        "createdBefore": Union[datetime, str],
    },
    total=False,
)

_RequiredImportReferenceJobItemTypeDef = TypedDict(
    "_RequiredImportReferenceJobItemTypeDef",
    {
        "id": str,
        "referenceStoreId": str,
        "roleArn": str,
        "status": ReferenceImportJobStatusType,
        "creationTime": datetime,
    },
)
_OptionalImportReferenceJobItemTypeDef = TypedDict(
    "_OptionalImportReferenceJobItemTypeDef",
    {
        "completionTime": datetime,
    },
    total=False,
)

class ImportReferenceJobItemTypeDef(
    _RequiredImportReferenceJobItemTypeDef, _OptionalImportReferenceJobItemTypeDef
):
    pass

ListAnnotationImportJobsFilterTypeDef = TypedDict(
    "ListAnnotationImportJobsFilterTypeDef",
    {
        "status": JobStatusType,
        "storeName": str,
    },
    total=False,
)

ListAnnotationStoresFilterTypeDef = TypedDict(
    "ListAnnotationStoresFilterTypeDef",
    {
        "status": StoreStatusType,
    },
    total=False,
)

_RequiredListMultipartReadSetUploadsRequestListMultipartReadSetUploadsPaginateTypeDef = TypedDict(
    "_RequiredListMultipartReadSetUploadsRequestListMultipartReadSetUploadsPaginateTypeDef",
    {
        "sequenceStoreId": str,
    },
)
_OptionalListMultipartReadSetUploadsRequestListMultipartReadSetUploadsPaginateTypeDef = TypedDict(
    "_OptionalListMultipartReadSetUploadsRequestListMultipartReadSetUploadsPaginateTypeDef",
    {
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

class ListMultipartReadSetUploadsRequestListMultipartReadSetUploadsPaginateTypeDef(
    _RequiredListMultipartReadSetUploadsRequestListMultipartReadSetUploadsPaginateTypeDef,
    _OptionalListMultipartReadSetUploadsRequestListMultipartReadSetUploadsPaginateTypeDef,
):
    pass

_RequiredListMultipartReadSetUploadsRequestRequestTypeDef = TypedDict(
    "_RequiredListMultipartReadSetUploadsRequestRequestTypeDef",
    {
        "sequenceStoreId": str,
    },
)
_OptionalListMultipartReadSetUploadsRequestRequestTypeDef = TypedDict(
    "_OptionalListMultipartReadSetUploadsRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)

class ListMultipartReadSetUploadsRequestRequestTypeDef(
    _RequiredListMultipartReadSetUploadsRequestRequestTypeDef,
    _OptionalListMultipartReadSetUploadsRequestRequestTypeDef,
):
    pass

_RequiredMultipartReadSetUploadListItemTypeDef = TypedDict(
    "_RequiredMultipartReadSetUploadListItemTypeDef",
    {
        "sequenceStoreId": str,
        "uploadId": str,
        "sourceFileType": FileTypeType,
        "subjectId": str,
        "sampleId": str,
        "generatedFrom": str,
        "referenceArn": str,
        "creationTime": datetime,
    },
)
_OptionalMultipartReadSetUploadListItemTypeDef = TypedDict(
    "_OptionalMultipartReadSetUploadListItemTypeDef",
    {
        "name": str,
        "description": str,
        "tags": Dict[str, str],
    },
    total=False,
)

class MultipartReadSetUploadListItemTypeDef(
    _RequiredMultipartReadSetUploadListItemTypeDef, _OptionalMultipartReadSetUploadListItemTypeDef
):
    pass

ReadSetUploadPartListFilterTypeDef = TypedDict(
    "ReadSetUploadPartListFilterTypeDef",
    {
        "createdAfter": Union[datetime, str],
        "createdBefore": Union[datetime, str],
    },
    total=False,
)

_RequiredReadSetUploadPartListItemTypeDef = TypedDict(
    "_RequiredReadSetUploadPartListItemTypeDef",
    {
        "partNumber": int,
        "partSize": int,
        "partSource": ReadSetPartSourceType,
        "checksum": str,
    },
)
_OptionalReadSetUploadPartListItemTypeDef = TypedDict(
    "_OptionalReadSetUploadPartListItemTypeDef",
    {
        "creationTime": datetime,
        "lastUpdatedTime": datetime,
    },
    total=False,
)

class ReadSetUploadPartListItemTypeDef(
    _RequiredReadSetUploadPartListItemTypeDef, _OptionalReadSetUploadPartListItemTypeDef
):
    pass

ReadSetFilterTypeDef = TypedDict(
    "ReadSetFilterTypeDef",
    {
        "name": str,
        "status": ReadSetStatusType,
        "referenceArn": str,
        "createdAfter": Union[datetime, str],
        "createdBefore": Union[datetime, str],
        "sampleId": str,
        "subjectId": str,
        "generatedFrom": str,
    },
    total=False,
)

ReferenceStoreFilterTypeDef = TypedDict(
    "ReferenceStoreFilterTypeDef",
    {
        "name": str,
        "createdAfter": Union[datetime, str],
        "createdBefore": Union[datetime, str],
    },
    total=False,
)

ReferenceFilterTypeDef = TypedDict(
    "ReferenceFilterTypeDef",
    {
        "name": str,
        "md5": str,
        "createdAfter": Union[datetime, str],
        "createdBefore": Union[datetime, str],
    },
    total=False,
)

_RequiredReferenceListItemTypeDef = TypedDict(
    "_RequiredReferenceListItemTypeDef",
    {
        "id": str,
        "arn": str,
        "referenceStoreId": str,
        "md5": str,
        "creationTime": datetime,
        "updateTime": datetime,
    },
)
_OptionalReferenceListItemTypeDef = TypedDict(
    "_OptionalReferenceListItemTypeDef",
    {
        "status": ReferenceStatusType,
        "name": str,
        "description": str,
    },
    total=False,
)

class ReferenceListItemTypeDef(
    _RequiredReferenceListItemTypeDef, _OptionalReferenceListItemTypeDef
):
    pass

ListRunGroupsRequestListRunGroupsPaginateTypeDef = TypedDict(
    "ListRunGroupsRequestListRunGroupsPaginateTypeDef",
    {
        "name": str,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

ListRunGroupsRequestRequestTypeDef = TypedDict(
    "ListRunGroupsRequestRequestTypeDef",
    {
        "name": str,
        "startingToken": str,
        "maxResults": int,
    },
    total=False,
)

RunGroupListItemTypeDef = TypedDict(
    "RunGroupListItemTypeDef",
    {
        "arn": str,
        "id": str,
        "name": str,
        "maxCpus": int,
        "maxRuns": int,
        "maxDuration": int,
        "creationTime": datetime,
        "maxGpus": int,
    },
    total=False,
)

_RequiredListRunTasksRequestListRunTasksPaginateTypeDef = TypedDict(
    "_RequiredListRunTasksRequestListRunTasksPaginateTypeDef",
    {
        "id": str,
    },
)
_OptionalListRunTasksRequestListRunTasksPaginateTypeDef = TypedDict(
    "_OptionalListRunTasksRequestListRunTasksPaginateTypeDef",
    {
        "status": TaskStatusType,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

class ListRunTasksRequestListRunTasksPaginateTypeDef(
    _RequiredListRunTasksRequestListRunTasksPaginateTypeDef,
    _OptionalListRunTasksRequestListRunTasksPaginateTypeDef,
):
    pass

_RequiredListRunTasksRequestRequestTypeDef = TypedDict(
    "_RequiredListRunTasksRequestRequestTypeDef",
    {
        "id": str,
    },
)
_OptionalListRunTasksRequestRequestTypeDef = TypedDict(
    "_OptionalListRunTasksRequestRequestTypeDef",
    {
        "status": TaskStatusType,
        "startingToken": str,
        "maxResults": int,
    },
    total=False,
)

class ListRunTasksRequestRequestTypeDef(
    _RequiredListRunTasksRequestRequestTypeDef, _OptionalListRunTasksRequestRequestTypeDef
):
    pass

TaskListItemTypeDef = TypedDict(
    "TaskListItemTypeDef",
    {
        "taskId": str,
        "status": TaskStatusType,
        "name": str,
        "cpus": int,
        "memory": int,
        "creationTime": datetime,
        "startTime": datetime,
        "stopTime": datetime,
        "gpus": int,
    },
    total=False,
)

ListRunsRequestListRunsPaginateTypeDef = TypedDict(
    "ListRunsRequestListRunsPaginateTypeDef",
    {
        "name": str,
        "runGroupId": str,
        "status": RunStatusType,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

ListRunsRequestRequestTypeDef = TypedDict(
    "ListRunsRequestRequestTypeDef",
    {
        "name": str,
        "runGroupId": str,
        "startingToken": str,
        "maxResults": int,
        "status": RunStatusType,
    },
    total=False,
)

RunListItemTypeDef = TypedDict(
    "RunListItemTypeDef",
    {
        "arn": str,
        "id": str,
        "status": RunStatusType,
        "workflowId": str,
        "name": str,
        "priority": int,
        "storageCapacity": int,
        "creationTime": datetime,
        "startTime": datetime,
        "stopTime": datetime,
    },
    total=False,
)

SequenceStoreFilterTypeDef = TypedDict(
    "SequenceStoreFilterTypeDef",
    {
        "name": str,
        "createdAfter": Union[datetime, str],
        "createdBefore": Union[datetime, str],
    },
    total=False,
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListVariantImportJobsFilterTypeDef = TypedDict(
    "ListVariantImportJobsFilterTypeDef",
    {
        "status": JobStatusType,
        "storeName": str,
    },
    total=False,
)

_RequiredVariantImportJobItemTypeDef = TypedDict(
    "_RequiredVariantImportJobItemTypeDef",
    {
        "id": str,
        "destinationName": str,
        "roleArn": str,
        "status": JobStatusType,
        "creationTime": datetime,
        "updateTime": datetime,
    },
)
_OptionalVariantImportJobItemTypeDef = TypedDict(
    "_OptionalVariantImportJobItemTypeDef",
    {
        "completionTime": datetime,
        "runLeftNormalization": bool,
        "annotationFields": Dict[str, str],
    },
    total=False,
)

class VariantImportJobItemTypeDef(
    _RequiredVariantImportJobItemTypeDef, _OptionalVariantImportJobItemTypeDef
):
    pass

ListVariantStoresFilterTypeDef = TypedDict(
    "ListVariantStoresFilterTypeDef",
    {
        "status": StoreStatusType,
    },
    total=False,
)

ListWorkflowsRequestListWorkflowsPaginateTypeDef = TypedDict(
    "ListWorkflowsRequestListWorkflowsPaginateTypeDef",
    {
        "type": WorkflowTypeType,
        "name": str,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

ListWorkflowsRequestRequestTypeDef = TypedDict(
    "ListWorkflowsRequestRequestTypeDef",
    {
        "type": WorkflowTypeType,
        "name": str,
        "startingToken": str,
        "maxResults": int,
    },
    total=False,
)

WorkflowListItemTypeDef = TypedDict(
    "WorkflowListItemTypeDef",
    {
        "arn": str,
        "id": str,
        "name": str,
        "status": WorkflowStatusType,
        "type": WorkflowTypeType,
        "digest": str,
        "creationTime": datetime,
        "metadata": Dict[str, str],
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

ReadOptionsTypeDef = TypedDict(
    "ReadOptionsTypeDef",
    {
        "sep": str,
        "encoding": str,
        "quote": str,
        "quoteAll": bool,
        "escape": str,
        "escapeQuotes": bool,
        "comment": str,
        "header": bool,
        "lineSep": str,
    },
    total=False,
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

StartAnnotationImportResponseTypeDef = TypedDict(
    "StartAnnotationImportResponseTypeDef",
    {
        "jobId": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

StartReadSetActivationJobSourceItemTypeDef = TypedDict(
    "StartReadSetActivationJobSourceItemTypeDef",
    {
        "readSetId": str,
    },
)

StartReadSetActivationJobResponseTypeDef = TypedDict(
    "StartReadSetActivationJobResponseTypeDef",
    {
        "id": str,
        "sequenceStoreId": str,
        "status": ReadSetActivationJobStatusType,
        "creationTime": datetime,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

StartReadSetExportJobResponseTypeDef = TypedDict(
    "StartReadSetExportJobResponseTypeDef",
    {
        "id": str,
        "sequenceStoreId": str,
        "destination": str,
        "status": ReadSetExportJobStatusType,
        "creationTime": datetime,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

StartReadSetImportJobResponseTypeDef = TypedDict(
    "StartReadSetImportJobResponseTypeDef",
    {
        "id": str,
        "sequenceStoreId": str,
        "roleArn": str,
        "status": ReadSetImportJobStatusType,
        "creationTime": datetime,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredStartReferenceImportJobSourceItemTypeDef = TypedDict(
    "_RequiredStartReferenceImportJobSourceItemTypeDef",
    {
        "sourceFile": str,
        "name": str,
    },
)
_OptionalStartReferenceImportJobSourceItemTypeDef = TypedDict(
    "_OptionalStartReferenceImportJobSourceItemTypeDef",
    {
        "description": str,
        "tags": Mapping[str, str],
    },
    total=False,
)

class StartReferenceImportJobSourceItemTypeDef(
    _RequiredStartReferenceImportJobSourceItemTypeDef,
    _OptionalStartReferenceImportJobSourceItemTypeDef,
):
    pass

StartReferenceImportJobResponseTypeDef = TypedDict(
    "StartReferenceImportJobResponseTypeDef",
    {
        "id": str,
        "referenceStoreId": str,
        "roleArn": str,
        "status": ReferenceImportJobStatusType,
        "creationTime": datetime,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredStartRunRequestRequestTypeDef = TypedDict(
    "_RequiredStartRunRequestRequestTypeDef",
    {
        "roleArn": str,
        "requestId": str,
    },
)
_OptionalStartRunRequestRequestTypeDef = TypedDict(
    "_OptionalStartRunRequestRequestTypeDef",
    {
        "workflowId": str,
        "workflowType": WorkflowTypeType,
        "runId": str,
        "name": str,
        "runGroupId": str,
        "priority": int,
        "parameters": Mapping[str, Any],
        "storageCapacity": int,
        "outputUri": str,
        "logLevel": RunLogLevelType,
        "tags": Mapping[str, str],
    },
    total=False,
)

class StartRunRequestRequestTypeDef(
    _RequiredStartRunRequestRequestTypeDef, _OptionalStartRunRequestRequestTypeDef
):
    pass

StartRunResponseTypeDef = TypedDict(
    "StartRunResponseTypeDef",
    {
        "arn": str,
        "id": str,
        "status": RunStatusType,
        "tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

VariantImportItemSourceTypeDef = TypedDict(
    "VariantImportItemSourceTypeDef",
    {
        "source": str,
    },
)

StartVariantImportResponseTypeDef = TypedDict(
    "StartVariantImportResponseTypeDef",
    {
        "jobId": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

TsvStoreOptionsTypeDef = TypedDict(
    "TsvStoreOptionsTypeDef",
    {
        "annotationType": AnnotationTypeType,
        "formatToHeader": Mapping[FormatToHeaderKeyType, str],
        "schema": Sequence[Mapping[str, SchemaValueTypeType]],
    },
    total=False,
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)

_RequiredUpdateAnnotationStoreRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateAnnotationStoreRequestRequestTypeDef",
    {
        "name": str,
    },
)
_OptionalUpdateAnnotationStoreRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateAnnotationStoreRequestRequestTypeDef",
    {
        "description": str,
    },
    total=False,
)

class UpdateAnnotationStoreRequestRequestTypeDef(
    _RequiredUpdateAnnotationStoreRequestRequestTypeDef,
    _OptionalUpdateAnnotationStoreRequestRequestTypeDef,
):
    pass

_RequiredUpdateRunGroupRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateRunGroupRequestRequestTypeDef",
    {
        "id": str,
    },
)
_OptionalUpdateRunGroupRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateRunGroupRequestRequestTypeDef",
    {
        "name": str,
        "maxCpus": int,
        "maxRuns": int,
        "maxDuration": int,
        "maxGpus": int,
    },
    total=False,
)

class UpdateRunGroupRequestRequestTypeDef(
    _RequiredUpdateRunGroupRequestRequestTypeDef, _OptionalUpdateRunGroupRequestRequestTypeDef
):
    pass

_RequiredUpdateVariantStoreRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateVariantStoreRequestRequestTypeDef",
    {
        "name": str,
    },
)
_OptionalUpdateVariantStoreRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateVariantStoreRequestRequestTypeDef",
    {
        "description": str,
    },
    total=False,
)

class UpdateVariantStoreRequestRequestTypeDef(
    _RequiredUpdateVariantStoreRequestRequestTypeDef,
    _OptionalUpdateVariantStoreRequestRequestTypeDef,
):
    pass

_RequiredUpdateWorkflowRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateWorkflowRequestRequestTypeDef",
    {
        "id": str,
    },
)
_OptionalUpdateWorkflowRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateWorkflowRequestRequestTypeDef",
    {
        "name": str,
        "description": str,
    },
    total=False,
)

class UpdateWorkflowRequestRequestTypeDef(
    _RequiredUpdateWorkflowRequestRequestTypeDef, _OptionalUpdateWorkflowRequestRequestTypeDef
):
    pass

UploadReadSetPartRequestRequestTypeDef = TypedDict(
    "UploadReadSetPartRequestRequestTypeDef",
    {
        "sequenceStoreId": str,
        "uploadId": str,
        "partSource": ReadSetPartSourceType,
        "partNumber": int,
        "payload": Union[str, bytes, IO[Any], StreamingBody],
    },
)

UploadReadSetPartResponseTypeDef = TypedDict(
    "UploadReadSetPartResponseTypeDef",
    {
        "checksum": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListReadSetActivationJobsRequestListReadSetActivationJobsPaginateTypeDef = TypedDict(
    "_RequiredListReadSetActivationJobsRequestListReadSetActivationJobsPaginateTypeDef",
    {
        "sequenceStoreId": str,
    },
)
_OptionalListReadSetActivationJobsRequestListReadSetActivationJobsPaginateTypeDef = TypedDict(
    "_OptionalListReadSetActivationJobsRequestListReadSetActivationJobsPaginateTypeDef",
    {
        "filter": ActivateReadSetFilterTypeDef,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

class ListReadSetActivationJobsRequestListReadSetActivationJobsPaginateTypeDef(
    _RequiredListReadSetActivationJobsRequestListReadSetActivationJobsPaginateTypeDef,
    _OptionalListReadSetActivationJobsRequestListReadSetActivationJobsPaginateTypeDef,
):
    pass

_RequiredListReadSetActivationJobsRequestRequestTypeDef = TypedDict(
    "_RequiredListReadSetActivationJobsRequestRequestTypeDef",
    {
        "sequenceStoreId": str,
    },
)
_OptionalListReadSetActivationJobsRequestRequestTypeDef = TypedDict(
    "_OptionalListReadSetActivationJobsRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
        "filter": ActivateReadSetFilterTypeDef,
    },
    total=False,
)

class ListReadSetActivationJobsRequestRequestTypeDef(
    _RequiredListReadSetActivationJobsRequestRequestTypeDef,
    _OptionalListReadSetActivationJobsRequestRequestTypeDef,
):
    pass

ListReadSetActivationJobsResponseTypeDef = TypedDict(
    "ListReadSetActivationJobsResponseTypeDef",
    {
        "nextToken": str,
        "activationJobs": List[ActivateReadSetJobItemTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetReadSetActivationJobResponseTypeDef = TypedDict(
    "GetReadSetActivationJobResponseTypeDef",
    {
        "id": str,
        "sequenceStoreId": str,
        "status": ReadSetActivationJobStatusType,
        "statusMessage": str,
        "creationTime": datetime,
        "completionTime": datetime,
        "sources": List[ActivateReadSetSourceItemTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListAnnotationImportJobsResponseTypeDef = TypedDict(
    "ListAnnotationImportJobsResponseTypeDef",
    {
        "annotationImportJobs": List[AnnotationImportJobItemTypeDef],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

CreateVariantStoreResponseTypeDef = TypedDict(
    "CreateVariantStoreResponseTypeDef",
    {
        "id": str,
        "reference": ReferenceItemTypeDef,
        "status": StoreStatusType,
        "name": str,
        "creationTime": datetime,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

UpdateVariantStoreResponseTypeDef = TypedDict(
    "UpdateVariantStoreResponseTypeDef",
    {
        "id": str,
        "reference": ReferenceItemTypeDef,
        "status": StoreStatusType,
        "name": str,
        "description": str,
        "creationTime": datetime,
        "updateTime": datetime,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

AnnotationStoreItemTypeDef = TypedDict(
    "AnnotationStoreItemTypeDef",
    {
        "id": str,
        "reference": ReferenceItemTypeDef,
        "status": StoreStatusType,
        "storeArn": str,
        "name": str,
        "storeFormat": StoreFormatType,
        "description": str,
        "sseConfig": SseConfigTypeDef,
        "creationTime": datetime,
        "updateTime": datetime,
        "statusMessage": str,
        "storeSizeBytes": int,
    },
)

_RequiredCreateReferenceStoreRequestRequestTypeDef = TypedDict(
    "_RequiredCreateReferenceStoreRequestRequestTypeDef",
    {
        "name": str,
    },
)
_OptionalCreateReferenceStoreRequestRequestTypeDef = TypedDict(
    "_OptionalCreateReferenceStoreRequestRequestTypeDef",
    {
        "description": str,
        "sseConfig": SseConfigTypeDef,
        "tags": Mapping[str, str],
        "clientToken": str,
    },
    total=False,
)

class CreateReferenceStoreRequestRequestTypeDef(
    _RequiredCreateReferenceStoreRequestRequestTypeDef,
    _OptionalCreateReferenceStoreRequestRequestTypeDef,
):
    pass

CreateReferenceStoreResponseTypeDef = TypedDict(
    "CreateReferenceStoreResponseTypeDef",
    {
        "id": str,
        "arn": str,
        "name": str,
        "description": str,
        "sseConfig": SseConfigTypeDef,
        "creationTime": datetime,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateSequenceStoreRequestRequestTypeDef = TypedDict(
    "_RequiredCreateSequenceStoreRequestRequestTypeDef",
    {
        "name": str,
    },
)
_OptionalCreateSequenceStoreRequestRequestTypeDef = TypedDict(
    "_OptionalCreateSequenceStoreRequestRequestTypeDef",
    {
        "description": str,
        "sseConfig": SseConfigTypeDef,
        "tags": Mapping[str, str],
        "clientToken": str,
        "fallbackLocation": str,
    },
    total=False,
)

class CreateSequenceStoreRequestRequestTypeDef(
    _RequiredCreateSequenceStoreRequestRequestTypeDef,
    _OptionalCreateSequenceStoreRequestRequestTypeDef,
):
    pass

CreateSequenceStoreResponseTypeDef = TypedDict(
    "CreateSequenceStoreResponseTypeDef",
    {
        "id": str,
        "arn": str,
        "name": str,
        "description": str,
        "sseConfig": SseConfigTypeDef,
        "creationTime": datetime,
        "fallbackLocation": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateVariantStoreRequestRequestTypeDef = TypedDict(
    "_RequiredCreateVariantStoreRequestRequestTypeDef",
    {
        "reference": ReferenceItemTypeDef,
    },
)
_OptionalCreateVariantStoreRequestRequestTypeDef = TypedDict(
    "_OptionalCreateVariantStoreRequestRequestTypeDef",
    {
        "name": str,
        "description": str,
        "tags": Mapping[str, str],
        "sseConfig": SseConfigTypeDef,
    },
    total=False,
)

class CreateVariantStoreRequestRequestTypeDef(
    _RequiredCreateVariantStoreRequestRequestTypeDef,
    _OptionalCreateVariantStoreRequestRequestTypeDef,
):
    pass

GetReferenceStoreResponseTypeDef = TypedDict(
    "GetReferenceStoreResponseTypeDef",
    {
        "id": str,
        "arn": str,
        "name": str,
        "description": str,
        "sseConfig": SseConfigTypeDef,
        "creationTime": datetime,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetSequenceStoreResponseTypeDef = TypedDict(
    "GetSequenceStoreResponseTypeDef",
    {
        "id": str,
        "arn": str,
        "name": str,
        "description": str,
        "sseConfig": SseConfigTypeDef,
        "creationTime": datetime,
        "fallbackLocation": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetVariantStoreResponseTypeDef = TypedDict(
    "GetVariantStoreResponseTypeDef",
    {
        "id": str,
        "reference": ReferenceItemTypeDef,
        "status": StoreStatusType,
        "storeArn": str,
        "name": str,
        "description": str,
        "sseConfig": SseConfigTypeDef,
        "creationTime": datetime,
        "updateTime": datetime,
        "tags": Dict[str, str],
        "statusMessage": str,
        "storeSizeBytes": int,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredReferenceStoreDetailTypeDef = TypedDict(
    "_RequiredReferenceStoreDetailTypeDef",
    {
        "arn": str,
        "id": str,
        "creationTime": datetime,
    },
)
_OptionalReferenceStoreDetailTypeDef = TypedDict(
    "_OptionalReferenceStoreDetailTypeDef",
    {
        "name": str,
        "description": str,
        "sseConfig": SseConfigTypeDef,
    },
    total=False,
)

class ReferenceStoreDetailTypeDef(
    _RequiredReferenceStoreDetailTypeDef, _OptionalReferenceStoreDetailTypeDef
):
    pass

_RequiredSequenceStoreDetailTypeDef = TypedDict(
    "_RequiredSequenceStoreDetailTypeDef",
    {
        "arn": str,
        "id": str,
        "creationTime": datetime,
    },
)
_OptionalSequenceStoreDetailTypeDef = TypedDict(
    "_OptionalSequenceStoreDetailTypeDef",
    {
        "name": str,
        "description": str,
        "sseConfig": SseConfigTypeDef,
        "fallbackLocation": str,
    },
    total=False,
)

class SequenceStoreDetailTypeDef(
    _RequiredSequenceStoreDetailTypeDef, _OptionalSequenceStoreDetailTypeDef
):
    pass

VariantStoreItemTypeDef = TypedDict(
    "VariantStoreItemTypeDef",
    {
        "id": str,
        "reference": ReferenceItemTypeDef,
        "status": StoreStatusType,
        "storeArn": str,
        "name": str,
        "description": str,
        "sseConfig": SseConfigTypeDef,
        "creationTime": datetime,
        "updateTime": datetime,
        "statusMessage": str,
        "storeSizeBytes": int,
    },
)

BatchDeleteReadSetResponseTypeDef = TypedDict(
    "BatchDeleteReadSetResponseTypeDef",
    {
        "errors": List[ReadSetBatchErrorTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

CompleteMultipartReadSetUploadRequestRequestTypeDef = TypedDict(
    "CompleteMultipartReadSetUploadRequestRequestTypeDef",
    {
        "sequenceStoreId": str,
        "uploadId": str,
        "parts": Sequence[CompleteReadSetUploadPartListItemTypeDef],
    },
)

_RequiredCreateWorkflowRequestRequestTypeDef = TypedDict(
    "_RequiredCreateWorkflowRequestRequestTypeDef",
    {
        "requestId": str,
    },
)
_OptionalCreateWorkflowRequestRequestTypeDef = TypedDict(
    "_OptionalCreateWorkflowRequestRequestTypeDef",
    {
        "name": str,
        "description": str,
        "engine": WorkflowEngineType,
        "definitionZip": Union[str, bytes, IO[Any], StreamingBody],
        "definitionUri": str,
        "main": str,
        "parameterTemplate": Mapping[str, WorkflowParameterTypeDef],
        "storageCapacity": int,
        "tags": Mapping[str, str],
        "accelerators": Literal["GPU"],
    },
    total=False,
)

class CreateWorkflowRequestRequestTypeDef(
    _RequiredCreateWorkflowRequestRequestTypeDef, _OptionalCreateWorkflowRequestRequestTypeDef
):
    pass

GetWorkflowResponseTypeDef = TypedDict(
    "GetWorkflowResponseTypeDef",
    {
        "arn": str,
        "id": str,
        "status": WorkflowStatusType,
        "type": WorkflowTypeType,
        "name": str,
        "description": str,
        "engine": WorkflowEngineType,
        "definition": str,
        "main": str,
        "digest": str,
        "parameterTemplate": Dict[str, WorkflowParameterTypeDef],
        "storageCapacity": int,
        "creationTime": datetime,
        "statusMessage": str,
        "tags": Dict[str, str],
        "metadata": Dict[str, str],
        "accelerators": Literal["GPU"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetReadSetExportJobResponseTypeDef = TypedDict(
    "GetReadSetExportJobResponseTypeDef",
    {
        "id": str,
        "sequenceStoreId": str,
        "destination": str,
        "status": ReadSetExportJobStatusType,
        "statusMessage": str,
        "creationTime": datetime,
        "completionTime": datetime,
        "readSets": List[ExportReadSetDetailTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListReadSetExportJobsRequestListReadSetExportJobsPaginateTypeDef = TypedDict(
    "_RequiredListReadSetExportJobsRequestListReadSetExportJobsPaginateTypeDef",
    {
        "sequenceStoreId": str,
    },
)
_OptionalListReadSetExportJobsRequestListReadSetExportJobsPaginateTypeDef = TypedDict(
    "_OptionalListReadSetExportJobsRequestListReadSetExportJobsPaginateTypeDef",
    {
        "filter": ExportReadSetFilterTypeDef,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

class ListReadSetExportJobsRequestListReadSetExportJobsPaginateTypeDef(
    _RequiredListReadSetExportJobsRequestListReadSetExportJobsPaginateTypeDef,
    _OptionalListReadSetExportJobsRequestListReadSetExportJobsPaginateTypeDef,
):
    pass

_RequiredListReadSetExportJobsRequestRequestTypeDef = TypedDict(
    "_RequiredListReadSetExportJobsRequestRequestTypeDef",
    {
        "sequenceStoreId": str,
    },
)
_OptionalListReadSetExportJobsRequestRequestTypeDef = TypedDict(
    "_OptionalListReadSetExportJobsRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
        "filter": ExportReadSetFilterTypeDef,
    },
    total=False,
)

class ListReadSetExportJobsRequestRequestTypeDef(
    _RequiredListReadSetExportJobsRequestRequestTypeDef,
    _OptionalListReadSetExportJobsRequestRequestTypeDef,
):
    pass

ListReadSetExportJobsResponseTypeDef = TypedDict(
    "ListReadSetExportJobsResponseTypeDef",
    {
        "nextToken": str,
        "exportJobs": List[ExportReadSetJobDetailTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredStartReadSetExportJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartReadSetExportJobRequestRequestTypeDef",
    {
        "sequenceStoreId": str,
        "destination": str,
        "roleArn": str,
        "sources": Sequence[ExportReadSetTypeDef],
    },
)
_OptionalStartReadSetExportJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartReadSetExportJobRequestRequestTypeDef",
    {
        "clientToken": str,
    },
    total=False,
)

class StartReadSetExportJobRequestRequestTypeDef(
    _RequiredStartReadSetExportJobRequestRequestTypeDef,
    _OptionalStartReadSetExportJobRequestRequestTypeDef,
):
    pass

ReadSetFilesTypeDef = TypedDict(
    "ReadSetFilesTypeDef",
    {
        "source1": FileInformationTypeDef,
        "source2": FileInformationTypeDef,
        "index": FileInformationTypeDef,
    },
    total=False,
)

ReferenceFilesTypeDef = TypedDict(
    "ReferenceFilesTypeDef",
    {
        "source": FileInformationTypeDef,
        "index": FileInformationTypeDef,
    },
    total=False,
)

_RequiredGetAnnotationImportRequestAnnotationImportJobCreatedWaitTypeDef = TypedDict(
    "_RequiredGetAnnotationImportRequestAnnotationImportJobCreatedWaitTypeDef",
    {
        "jobId": str,
    },
)
_OptionalGetAnnotationImportRequestAnnotationImportJobCreatedWaitTypeDef = TypedDict(
    "_OptionalGetAnnotationImportRequestAnnotationImportJobCreatedWaitTypeDef",
    {
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

class GetAnnotationImportRequestAnnotationImportJobCreatedWaitTypeDef(
    _RequiredGetAnnotationImportRequestAnnotationImportJobCreatedWaitTypeDef,
    _OptionalGetAnnotationImportRequestAnnotationImportJobCreatedWaitTypeDef,
):
    pass

_RequiredGetAnnotationStoreRequestAnnotationStoreCreatedWaitTypeDef = TypedDict(
    "_RequiredGetAnnotationStoreRequestAnnotationStoreCreatedWaitTypeDef",
    {
        "name": str,
    },
)
_OptionalGetAnnotationStoreRequestAnnotationStoreCreatedWaitTypeDef = TypedDict(
    "_OptionalGetAnnotationStoreRequestAnnotationStoreCreatedWaitTypeDef",
    {
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

class GetAnnotationStoreRequestAnnotationStoreCreatedWaitTypeDef(
    _RequiredGetAnnotationStoreRequestAnnotationStoreCreatedWaitTypeDef,
    _OptionalGetAnnotationStoreRequestAnnotationStoreCreatedWaitTypeDef,
):
    pass

_RequiredGetAnnotationStoreRequestAnnotationStoreDeletedWaitTypeDef = TypedDict(
    "_RequiredGetAnnotationStoreRequestAnnotationStoreDeletedWaitTypeDef",
    {
        "name": str,
    },
)
_OptionalGetAnnotationStoreRequestAnnotationStoreDeletedWaitTypeDef = TypedDict(
    "_OptionalGetAnnotationStoreRequestAnnotationStoreDeletedWaitTypeDef",
    {
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

class GetAnnotationStoreRequestAnnotationStoreDeletedWaitTypeDef(
    _RequiredGetAnnotationStoreRequestAnnotationStoreDeletedWaitTypeDef,
    _OptionalGetAnnotationStoreRequestAnnotationStoreDeletedWaitTypeDef,
):
    pass

_RequiredGetReadSetActivationJobRequestReadSetActivationJobCompletedWaitTypeDef = TypedDict(
    "_RequiredGetReadSetActivationJobRequestReadSetActivationJobCompletedWaitTypeDef",
    {
        "id": str,
        "sequenceStoreId": str,
    },
)
_OptionalGetReadSetActivationJobRequestReadSetActivationJobCompletedWaitTypeDef = TypedDict(
    "_OptionalGetReadSetActivationJobRequestReadSetActivationJobCompletedWaitTypeDef",
    {
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

class GetReadSetActivationJobRequestReadSetActivationJobCompletedWaitTypeDef(
    _RequiredGetReadSetActivationJobRequestReadSetActivationJobCompletedWaitTypeDef,
    _OptionalGetReadSetActivationJobRequestReadSetActivationJobCompletedWaitTypeDef,
):
    pass

_RequiredGetReadSetExportJobRequestReadSetExportJobCompletedWaitTypeDef = TypedDict(
    "_RequiredGetReadSetExportJobRequestReadSetExportJobCompletedWaitTypeDef",
    {
        "sequenceStoreId": str,
        "id": str,
    },
)
_OptionalGetReadSetExportJobRequestReadSetExportJobCompletedWaitTypeDef = TypedDict(
    "_OptionalGetReadSetExportJobRequestReadSetExportJobCompletedWaitTypeDef",
    {
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

class GetReadSetExportJobRequestReadSetExportJobCompletedWaitTypeDef(
    _RequiredGetReadSetExportJobRequestReadSetExportJobCompletedWaitTypeDef,
    _OptionalGetReadSetExportJobRequestReadSetExportJobCompletedWaitTypeDef,
):
    pass

_RequiredGetReadSetImportJobRequestReadSetImportJobCompletedWaitTypeDef = TypedDict(
    "_RequiredGetReadSetImportJobRequestReadSetImportJobCompletedWaitTypeDef",
    {
        "id": str,
        "sequenceStoreId": str,
    },
)
_OptionalGetReadSetImportJobRequestReadSetImportJobCompletedWaitTypeDef = TypedDict(
    "_OptionalGetReadSetImportJobRequestReadSetImportJobCompletedWaitTypeDef",
    {
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

class GetReadSetImportJobRequestReadSetImportJobCompletedWaitTypeDef(
    _RequiredGetReadSetImportJobRequestReadSetImportJobCompletedWaitTypeDef,
    _OptionalGetReadSetImportJobRequestReadSetImportJobCompletedWaitTypeDef,
):
    pass

_RequiredGetReferenceImportJobRequestReferenceImportJobCompletedWaitTypeDef = TypedDict(
    "_RequiredGetReferenceImportJobRequestReferenceImportJobCompletedWaitTypeDef",
    {
        "id": str,
        "referenceStoreId": str,
    },
)
_OptionalGetReferenceImportJobRequestReferenceImportJobCompletedWaitTypeDef = TypedDict(
    "_OptionalGetReferenceImportJobRequestReferenceImportJobCompletedWaitTypeDef",
    {
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

class GetReferenceImportJobRequestReferenceImportJobCompletedWaitTypeDef(
    _RequiredGetReferenceImportJobRequestReferenceImportJobCompletedWaitTypeDef,
    _OptionalGetReferenceImportJobRequestReferenceImportJobCompletedWaitTypeDef,
):
    pass

_RequiredGetRunRequestRunCompletedWaitTypeDef = TypedDict(
    "_RequiredGetRunRequestRunCompletedWaitTypeDef",
    {
        "id": str,
    },
)
_OptionalGetRunRequestRunCompletedWaitTypeDef = TypedDict(
    "_OptionalGetRunRequestRunCompletedWaitTypeDef",
    {
        "export": Sequence[Literal["DEFINITION"]],
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

class GetRunRequestRunCompletedWaitTypeDef(
    _RequiredGetRunRequestRunCompletedWaitTypeDef, _OptionalGetRunRequestRunCompletedWaitTypeDef
):
    pass

_RequiredGetRunRequestRunRunningWaitTypeDef = TypedDict(
    "_RequiredGetRunRequestRunRunningWaitTypeDef",
    {
        "id": str,
    },
)
_OptionalGetRunRequestRunRunningWaitTypeDef = TypedDict(
    "_OptionalGetRunRequestRunRunningWaitTypeDef",
    {
        "export": Sequence[Literal["DEFINITION"]],
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

class GetRunRequestRunRunningWaitTypeDef(
    _RequiredGetRunRequestRunRunningWaitTypeDef, _OptionalGetRunRequestRunRunningWaitTypeDef
):
    pass

_RequiredGetRunTaskRequestTaskCompletedWaitTypeDef = TypedDict(
    "_RequiredGetRunTaskRequestTaskCompletedWaitTypeDef",
    {
        "id": str,
        "taskId": str,
    },
)
_OptionalGetRunTaskRequestTaskCompletedWaitTypeDef = TypedDict(
    "_OptionalGetRunTaskRequestTaskCompletedWaitTypeDef",
    {
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

class GetRunTaskRequestTaskCompletedWaitTypeDef(
    _RequiredGetRunTaskRequestTaskCompletedWaitTypeDef,
    _OptionalGetRunTaskRequestTaskCompletedWaitTypeDef,
):
    pass

_RequiredGetRunTaskRequestTaskRunningWaitTypeDef = TypedDict(
    "_RequiredGetRunTaskRequestTaskRunningWaitTypeDef",
    {
        "id": str,
        "taskId": str,
    },
)
_OptionalGetRunTaskRequestTaskRunningWaitTypeDef = TypedDict(
    "_OptionalGetRunTaskRequestTaskRunningWaitTypeDef",
    {
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

class GetRunTaskRequestTaskRunningWaitTypeDef(
    _RequiredGetRunTaskRequestTaskRunningWaitTypeDef,
    _OptionalGetRunTaskRequestTaskRunningWaitTypeDef,
):
    pass

_RequiredGetVariantImportRequestVariantImportJobCreatedWaitTypeDef = TypedDict(
    "_RequiredGetVariantImportRequestVariantImportJobCreatedWaitTypeDef",
    {
        "jobId": str,
    },
)
_OptionalGetVariantImportRequestVariantImportJobCreatedWaitTypeDef = TypedDict(
    "_OptionalGetVariantImportRequestVariantImportJobCreatedWaitTypeDef",
    {
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

class GetVariantImportRequestVariantImportJobCreatedWaitTypeDef(
    _RequiredGetVariantImportRequestVariantImportJobCreatedWaitTypeDef,
    _OptionalGetVariantImportRequestVariantImportJobCreatedWaitTypeDef,
):
    pass

_RequiredGetVariantStoreRequestVariantStoreCreatedWaitTypeDef = TypedDict(
    "_RequiredGetVariantStoreRequestVariantStoreCreatedWaitTypeDef",
    {
        "name": str,
    },
)
_OptionalGetVariantStoreRequestVariantStoreCreatedWaitTypeDef = TypedDict(
    "_OptionalGetVariantStoreRequestVariantStoreCreatedWaitTypeDef",
    {
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

class GetVariantStoreRequestVariantStoreCreatedWaitTypeDef(
    _RequiredGetVariantStoreRequestVariantStoreCreatedWaitTypeDef,
    _OptionalGetVariantStoreRequestVariantStoreCreatedWaitTypeDef,
):
    pass

_RequiredGetVariantStoreRequestVariantStoreDeletedWaitTypeDef = TypedDict(
    "_RequiredGetVariantStoreRequestVariantStoreDeletedWaitTypeDef",
    {
        "name": str,
    },
)
_OptionalGetVariantStoreRequestVariantStoreDeletedWaitTypeDef = TypedDict(
    "_OptionalGetVariantStoreRequestVariantStoreDeletedWaitTypeDef",
    {
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

class GetVariantStoreRequestVariantStoreDeletedWaitTypeDef(
    _RequiredGetVariantStoreRequestVariantStoreDeletedWaitTypeDef,
    _OptionalGetVariantStoreRequestVariantStoreDeletedWaitTypeDef,
):
    pass

_RequiredGetWorkflowRequestWorkflowActiveWaitTypeDef = TypedDict(
    "_RequiredGetWorkflowRequestWorkflowActiveWaitTypeDef",
    {
        "id": str,
    },
)
_OptionalGetWorkflowRequestWorkflowActiveWaitTypeDef = TypedDict(
    "_OptionalGetWorkflowRequestWorkflowActiveWaitTypeDef",
    {
        "type": WorkflowTypeType,
        "export": Sequence[Literal["DEFINITION"]],
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

class GetWorkflowRequestWorkflowActiveWaitTypeDef(
    _RequiredGetWorkflowRequestWorkflowActiveWaitTypeDef,
    _OptionalGetWorkflowRequestWorkflowActiveWaitTypeDef,
):
    pass

_RequiredReadSetListItemTypeDef = TypedDict(
    "_RequiredReadSetListItemTypeDef",
    {
        "id": str,
        "arn": str,
        "sequenceStoreId": str,
        "status": ReadSetStatusType,
        "fileType": FileTypeType,
        "creationTime": datetime,
    },
)
_OptionalReadSetListItemTypeDef = TypedDict(
    "_OptionalReadSetListItemTypeDef",
    {
        "subjectId": str,
        "sampleId": str,
        "name": str,
        "description": str,
        "referenceArn": str,
        "sequenceInformation": SequenceInformationTypeDef,
        "statusMessage": str,
    },
    total=False,
)

class ReadSetListItemTypeDef(_RequiredReadSetListItemTypeDef, _OptionalReadSetListItemTypeDef):
    pass

GetReferenceImportJobResponseTypeDef = TypedDict(
    "GetReferenceImportJobResponseTypeDef",
    {
        "id": str,
        "referenceStoreId": str,
        "roleArn": str,
        "status": ReferenceImportJobStatusType,
        "statusMessage": str,
        "creationTime": datetime,
        "completionTime": datetime,
        "sources": List[ImportReferenceSourceItemTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetVariantImportResponseTypeDef = TypedDict(
    "GetVariantImportResponseTypeDef",
    {
        "id": str,
        "destinationName": str,
        "roleArn": str,
        "status": JobStatusType,
        "statusMessage": str,
        "creationTime": datetime,
        "updateTime": datetime,
        "completionTime": datetime,
        "items": List[VariantImportItemDetailTypeDef],
        "runLeftNormalization": bool,
        "annotationFields": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListReadSetImportJobsRequestListReadSetImportJobsPaginateTypeDef = TypedDict(
    "_RequiredListReadSetImportJobsRequestListReadSetImportJobsPaginateTypeDef",
    {
        "sequenceStoreId": str,
    },
)
_OptionalListReadSetImportJobsRequestListReadSetImportJobsPaginateTypeDef = TypedDict(
    "_OptionalListReadSetImportJobsRequestListReadSetImportJobsPaginateTypeDef",
    {
        "filter": ImportReadSetFilterTypeDef,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

class ListReadSetImportJobsRequestListReadSetImportJobsPaginateTypeDef(
    _RequiredListReadSetImportJobsRequestListReadSetImportJobsPaginateTypeDef,
    _OptionalListReadSetImportJobsRequestListReadSetImportJobsPaginateTypeDef,
):
    pass

_RequiredListReadSetImportJobsRequestRequestTypeDef = TypedDict(
    "_RequiredListReadSetImportJobsRequestRequestTypeDef",
    {
        "sequenceStoreId": str,
    },
)
_OptionalListReadSetImportJobsRequestRequestTypeDef = TypedDict(
    "_OptionalListReadSetImportJobsRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
        "filter": ImportReadSetFilterTypeDef,
    },
    total=False,
)

class ListReadSetImportJobsRequestRequestTypeDef(
    _RequiredListReadSetImportJobsRequestRequestTypeDef,
    _OptionalListReadSetImportJobsRequestRequestTypeDef,
):
    pass

ListReadSetImportJobsResponseTypeDef = TypedDict(
    "ListReadSetImportJobsResponseTypeDef",
    {
        "nextToken": str,
        "importJobs": List[ImportReadSetJobItemTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredImportReadSetSourceItemTypeDef = TypedDict(
    "_RequiredImportReadSetSourceItemTypeDef",
    {
        "sourceFiles": SourceFilesTypeDef,
        "sourceFileType": FileTypeType,
        "status": ReadSetImportJobItemStatusType,
        "subjectId": str,
        "sampleId": str,
    },
)
_OptionalImportReadSetSourceItemTypeDef = TypedDict(
    "_OptionalImportReadSetSourceItemTypeDef",
    {
        "statusMessage": str,
        "generatedFrom": str,
        "referenceArn": str,
        "name": str,
        "description": str,
        "tags": Dict[str, str],
    },
    total=False,
)

class ImportReadSetSourceItemTypeDef(
    _RequiredImportReadSetSourceItemTypeDef, _OptionalImportReadSetSourceItemTypeDef
):
    pass

_RequiredStartReadSetImportJobSourceItemTypeDef = TypedDict(
    "_RequiredStartReadSetImportJobSourceItemTypeDef",
    {
        "sourceFiles": SourceFilesTypeDef,
        "sourceFileType": FileTypeType,
        "subjectId": str,
        "sampleId": str,
        "referenceArn": str,
    },
)
_OptionalStartReadSetImportJobSourceItemTypeDef = TypedDict(
    "_OptionalStartReadSetImportJobSourceItemTypeDef",
    {
        "generatedFrom": str,
        "name": str,
        "description": str,
        "tags": Mapping[str, str],
    },
    total=False,
)

class StartReadSetImportJobSourceItemTypeDef(
    _RequiredStartReadSetImportJobSourceItemTypeDef, _OptionalStartReadSetImportJobSourceItemTypeDef
):
    pass

_RequiredListReferenceImportJobsRequestListReferenceImportJobsPaginateTypeDef = TypedDict(
    "_RequiredListReferenceImportJobsRequestListReferenceImportJobsPaginateTypeDef",
    {
        "referenceStoreId": str,
    },
)
_OptionalListReferenceImportJobsRequestListReferenceImportJobsPaginateTypeDef = TypedDict(
    "_OptionalListReferenceImportJobsRequestListReferenceImportJobsPaginateTypeDef",
    {
        "filter": ImportReferenceFilterTypeDef,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

class ListReferenceImportJobsRequestListReferenceImportJobsPaginateTypeDef(
    _RequiredListReferenceImportJobsRequestListReferenceImportJobsPaginateTypeDef,
    _OptionalListReferenceImportJobsRequestListReferenceImportJobsPaginateTypeDef,
):
    pass

_RequiredListReferenceImportJobsRequestRequestTypeDef = TypedDict(
    "_RequiredListReferenceImportJobsRequestRequestTypeDef",
    {
        "referenceStoreId": str,
    },
)
_OptionalListReferenceImportJobsRequestRequestTypeDef = TypedDict(
    "_OptionalListReferenceImportJobsRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
        "filter": ImportReferenceFilterTypeDef,
    },
    total=False,
)

class ListReferenceImportJobsRequestRequestTypeDef(
    _RequiredListReferenceImportJobsRequestRequestTypeDef,
    _OptionalListReferenceImportJobsRequestRequestTypeDef,
):
    pass

ListReferenceImportJobsResponseTypeDef = TypedDict(
    "ListReferenceImportJobsResponseTypeDef",
    {
        "nextToken": str,
        "importJobs": List[ImportReferenceJobItemTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListAnnotationImportJobsRequestListAnnotationImportJobsPaginateTypeDef = TypedDict(
    "ListAnnotationImportJobsRequestListAnnotationImportJobsPaginateTypeDef",
    {
        "ids": Sequence[str],
        "filter": ListAnnotationImportJobsFilterTypeDef,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

ListAnnotationImportJobsRequestRequestTypeDef = TypedDict(
    "ListAnnotationImportJobsRequestRequestTypeDef",
    {
        "maxResults": int,
        "ids": Sequence[str],
        "nextToken": str,
        "filter": ListAnnotationImportJobsFilterTypeDef,
    },
    total=False,
)

ListAnnotationStoresRequestListAnnotationStoresPaginateTypeDef = TypedDict(
    "ListAnnotationStoresRequestListAnnotationStoresPaginateTypeDef",
    {
        "ids": Sequence[str],
        "filter": ListAnnotationStoresFilterTypeDef,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

ListAnnotationStoresRequestRequestTypeDef = TypedDict(
    "ListAnnotationStoresRequestRequestTypeDef",
    {
        "ids": Sequence[str],
        "maxResults": int,
        "nextToken": str,
        "filter": ListAnnotationStoresFilterTypeDef,
    },
    total=False,
)

ListMultipartReadSetUploadsResponseTypeDef = TypedDict(
    "ListMultipartReadSetUploadsResponseTypeDef",
    {
        "nextToken": str,
        "uploads": List[MultipartReadSetUploadListItemTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListReadSetUploadPartsRequestListReadSetUploadPartsPaginateTypeDef = TypedDict(
    "_RequiredListReadSetUploadPartsRequestListReadSetUploadPartsPaginateTypeDef",
    {
        "sequenceStoreId": str,
        "uploadId": str,
        "partSource": ReadSetPartSourceType,
    },
)
_OptionalListReadSetUploadPartsRequestListReadSetUploadPartsPaginateTypeDef = TypedDict(
    "_OptionalListReadSetUploadPartsRequestListReadSetUploadPartsPaginateTypeDef",
    {
        "filter": ReadSetUploadPartListFilterTypeDef,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

class ListReadSetUploadPartsRequestListReadSetUploadPartsPaginateTypeDef(
    _RequiredListReadSetUploadPartsRequestListReadSetUploadPartsPaginateTypeDef,
    _OptionalListReadSetUploadPartsRequestListReadSetUploadPartsPaginateTypeDef,
):
    pass

_RequiredListReadSetUploadPartsRequestRequestTypeDef = TypedDict(
    "_RequiredListReadSetUploadPartsRequestRequestTypeDef",
    {
        "sequenceStoreId": str,
        "uploadId": str,
        "partSource": ReadSetPartSourceType,
    },
)
_OptionalListReadSetUploadPartsRequestRequestTypeDef = TypedDict(
    "_OptionalListReadSetUploadPartsRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
        "filter": ReadSetUploadPartListFilterTypeDef,
    },
    total=False,
)

class ListReadSetUploadPartsRequestRequestTypeDef(
    _RequiredListReadSetUploadPartsRequestRequestTypeDef,
    _OptionalListReadSetUploadPartsRequestRequestTypeDef,
):
    pass

ListReadSetUploadPartsResponseTypeDef = TypedDict(
    "ListReadSetUploadPartsResponseTypeDef",
    {
        "nextToken": str,
        "parts": List[ReadSetUploadPartListItemTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListReadSetsRequestListReadSetsPaginateTypeDef = TypedDict(
    "_RequiredListReadSetsRequestListReadSetsPaginateTypeDef",
    {
        "sequenceStoreId": str,
    },
)
_OptionalListReadSetsRequestListReadSetsPaginateTypeDef = TypedDict(
    "_OptionalListReadSetsRequestListReadSetsPaginateTypeDef",
    {
        "filter": ReadSetFilterTypeDef,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

class ListReadSetsRequestListReadSetsPaginateTypeDef(
    _RequiredListReadSetsRequestListReadSetsPaginateTypeDef,
    _OptionalListReadSetsRequestListReadSetsPaginateTypeDef,
):
    pass

_RequiredListReadSetsRequestRequestTypeDef = TypedDict(
    "_RequiredListReadSetsRequestRequestTypeDef",
    {
        "sequenceStoreId": str,
    },
)
_OptionalListReadSetsRequestRequestTypeDef = TypedDict(
    "_OptionalListReadSetsRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
        "filter": ReadSetFilterTypeDef,
    },
    total=False,
)

class ListReadSetsRequestRequestTypeDef(
    _RequiredListReadSetsRequestRequestTypeDef, _OptionalListReadSetsRequestRequestTypeDef
):
    pass

ListReferenceStoresRequestListReferenceStoresPaginateTypeDef = TypedDict(
    "ListReferenceStoresRequestListReferenceStoresPaginateTypeDef",
    {
        "filter": ReferenceStoreFilterTypeDef,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

ListReferenceStoresRequestRequestTypeDef = TypedDict(
    "ListReferenceStoresRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
        "filter": ReferenceStoreFilterTypeDef,
    },
    total=False,
)

_RequiredListReferencesRequestListReferencesPaginateTypeDef = TypedDict(
    "_RequiredListReferencesRequestListReferencesPaginateTypeDef",
    {
        "referenceStoreId": str,
    },
)
_OptionalListReferencesRequestListReferencesPaginateTypeDef = TypedDict(
    "_OptionalListReferencesRequestListReferencesPaginateTypeDef",
    {
        "filter": ReferenceFilterTypeDef,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

class ListReferencesRequestListReferencesPaginateTypeDef(
    _RequiredListReferencesRequestListReferencesPaginateTypeDef,
    _OptionalListReferencesRequestListReferencesPaginateTypeDef,
):
    pass

_RequiredListReferencesRequestRequestTypeDef = TypedDict(
    "_RequiredListReferencesRequestRequestTypeDef",
    {
        "referenceStoreId": str,
    },
)
_OptionalListReferencesRequestRequestTypeDef = TypedDict(
    "_OptionalListReferencesRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
        "filter": ReferenceFilterTypeDef,
    },
    total=False,
)

class ListReferencesRequestRequestTypeDef(
    _RequiredListReferencesRequestRequestTypeDef, _OptionalListReferencesRequestRequestTypeDef
):
    pass

ListReferencesResponseTypeDef = TypedDict(
    "ListReferencesResponseTypeDef",
    {
        "nextToken": str,
        "references": List[ReferenceListItemTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListRunGroupsResponseTypeDef = TypedDict(
    "ListRunGroupsResponseTypeDef",
    {
        "items": List[RunGroupListItemTypeDef],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListRunTasksResponseTypeDef = TypedDict(
    "ListRunTasksResponseTypeDef",
    {
        "items": List[TaskListItemTypeDef],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListRunsResponseTypeDef = TypedDict(
    "ListRunsResponseTypeDef",
    {
        "items": List[RunListItemTypeDef],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListSequenceStoresRequestListSequenceStoresPaginateTypeDef = TypedDict(
    "ListSequenceStoresRequestListSequenceStoresPaginateTypeDef",
    {
        "filter": SequenceStoreFilterTypeDef,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

ListSequenceStoresRequestRequestTypeDef = TypedDict(
    "ListSequenceStoresRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
        "filter": SequenceStoreFilterTypeDef,
    },
    total=False,
)

ListVariantImportJobsRequestListVariantImportJobsPaginateTypeDef = TypedDict(
    "ListVariantImportJobsRequestListVariantImportJobsPaginateTypeDef",
    {
        "ids": Sequence[str],
        "filter": ListVariantImportJobsFilterTypeDef,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

ListVariantImportJobsRequestRequestTypeDef = TypedDict(
    "ListVariantImportJobsRequestRequestTypeDef",
    {
        "maxResults": int,
        "ids": Sequence[str],
        "nextToken": str,
        "filter": ListVariantImportJobsFilterTypeDef,
    },
    total=False,
)

ListVariantImportJobsResponseTypeDef = TypedDict(
    "ListVariantImportJobsResponseTypeDef",
    {
        "variantImportJobs": List[VariantImportJobItemTypeDef],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListVariantStoresRequestListVariantStoresPaginateTypeDef = TypedDict(
    "ListVariantStoresRequestListVariantStoresPaginateTypeDef",
    {
        "ids": Sequence[str],
        "filter": ListVariantStoresFilterTypeDef,
        "PaginationConfig": "PaginatorConfigTypeDef",
    },
    total=False,
)

ListVariantStoresRequestRequestTypeDef = TypedDict(
    "ListVariantStoresRequestRequestTypeDef",
    {
        "maxResults": int,
        "ids": Sequence[str],
        "nextToken": str,
        "filter": ListVariantStoresFilterTypeDef,
    },
    total=False,
)

ListWorkflowsResponseTypeDef = TypedDict(
    "ListWorkflowsResponseTypeDef",
    {
        "items": List[WorkflowListItemTypeDef],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

TsvOptionsTypeDef = TypedDict(
    "TsvOptionsTypeDef",
    {
        "readOptions": ReadOptionsTypeDef,
    },
    total=False,
)

_RequiredStartReadSetActivationJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartReadSetActivationJobRequestRequestTypeDef",
    {
        "sequenceStoreId": str,
        "sources": Sequence[StartReadSetActivationJobSourceItemTypeDef],
    },
)
_OptionalStartReadSetActivationJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartReadSetActivationJobRequestRequestTypeDef",
    {
        "clientToken": str,
    },
    total=False,
)

class StartReadSetActivationJobRequestRequestTypeDef(
    _RequiredStartReadSetActivationJobRequestRequestTypeDef,
    _OptionalStartReadSetActivationJobRequestRequestTypeDef,
):
    pass

_RequiredStartReferenceImportJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartReferenceImportJobRequestRequestTypeDef",
    {
        "referenceStoreId": str,
        "roleArn": str,
        "sources": Sequence[StartReferenceImportJobSourceItemTypeDef],
    },
)
_OptionalStartReferenceImportJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartReferenceImportJobRequestRequestTypeDef",
    {
        "clientToken": str,
    },
    total=False,
)

class StartReferenceImportJobRequestRequestTypeDef(
    _RequiredStartReferenceImportJobRequestRequestTypeDef,
    _OptionalStartReferenceImportJobRequestRequestTypeDef,
):
    pass

_RequiredStartVariantImportRequestRequestTypeDef = TypedDict(
    "_RequiredStartVariantImportRequestRequestTypeDef",
    {
        "destinationName": str,
        "roleArn": str,
        "items": Sequence[VariantImportItemSourceTypeDef],
    },
)
_OptionalStartVariantImportRequestRequestTypeDef = TypedDict(
    "_OptionalStartVariantImportRequestRequestTypeDef",
    {
        "runLeftNormalization": bool,
        "annotationFields": Mapping[str, str],
    },
    total=False,
)

class StartVariantImportRequestRequestTypeDef(
    _RequiredStartVariantImportRequestRequestTypeDef,
    _OptionalStartVariantImportRequestRequestTypeDef,
):
    pass

StoreOptionsTypeDef = TypedDict(
    "StoreOptionsTypeDef",
    {
        "tsvStoreOptions": TsvStoreOptionsTypeDef,
    },
    total=False,
)

ListAnnotationStoresResponseTypeDef = TypedDict(
    "ListAnnotationStoresResponseTypeDef",
    {
        "annotationStores": List[AnnotationStoreItemTypeDef],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListReferenceStoresResponseTypeDef = TypedDict(
    "ListReferenceStoresResponseTypeDef",
    {
        "nextToken": str,
        "referenceStores": List[ReferenceStoreDetailTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListSequenceStoresResponseTypeDef = TypedDict(
    "ListSequenceStoresResponseTypeDef",
    {
        "nextToken": str,
        "sequenceStores": List[SequenceStoreDetailTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListVariantStoresResponseTypeDef = TypedDict(
    "ListVariantStoresResponseTypeDef",
    {
        "variantStores": List[VariantStoreItemTypeDef],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetReadSetMetadataResponseTypeDef = TypedDict(
    "GetReadSetMetadataResponseTypeDef",
    {
        "id": str,
        "arn": str,
        "sequenceStoreId": str,
        "subjectId": str,
        "sampleId": str,
        "status": ReadSetStatusType,
        "name": str,
        "description": str,
        "fileType": FileTypeType,
        "creationTime": datetime,
        "sequenceInformation": SequenceInformationTypeDef,
        "referenceArn": str,
        "files": ReadSetFilesTypeDef,
        "statusMessage": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetReferenceMetadataResponseTypeDef = TypedDict(
    "GetReferenceMetadataResponseTypeDef",
    {
        "id": str,
        "arn": str,
        "referenceStoreId": str,
        "md5": str,
        "status": ReferenceStatusType,
        "name": str,
        "description": str,
        "creationTime": datetime,
        "updateTime": datetime,
        "files": ReferenceFilesTypeDef,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListReadSetsResponseTypeDef = TypedDict(
    "ListReadSetsResponseTypeDef",
    {
        "nextToken": str,
        "readSets": List[ReadSetListItemTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetReadSetImportJobResponseTypeDef = TypedDict(
    "GetReadSetImportJobResponseTypeDef",
    {
        "id": str,
        "sequenceStoreId": str,
        "roleArn": str,
        "status": ReadSetImportJobStatusType,
        "statusMessage": str,
        "creationTime": datetime,
        "completionTime": datetime,
        "sources": List[ImportReadSetSourceItemTypeDef],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredStartReadSetImportJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartReadSetImportJobRequestRequestTypeDef",
    {
        "sequenceStoreId": str,
        "roleArn": str,
        "sources": Sequence[StartReadSetImportJobSourceItemTypeDef],
    },
)
_OptionalStartReadSetImportJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartReadSetImportJobRequestRequestTypeDef",
    {
        "clientToken": str,
    },
    total=False,
)

class StartReadSetImportJobRequestRequestTypeDef(
    _RequiredStartReadSetImportJobRequestRequestTypeDef,
    _OptionalStartReadSetImportJobRequestRequestTypeDef,
):
    pass

FormatOptionsTypeDef = TypedDict(
    "FormatOptionsTypeDef",
    {
        "tsvOptions": TsvOptionsTypeDef,
        "vcfOptions": VcfOptionsTypeDef,
    },
    total=False,
)

_RequiredCreateAnnotationStoreRequestRequestTypeDef = TypedDict(
    "_RequiredCreateAnnotationStoreRequestRequestTypeDef",
    {
        "storeFormat": StoreFormatType,
    },
)
_OptionalCreateAnnotationStoreRequestRequestTypeDef = TypedDict(
    "_OptionalCreateAnnotationStoreRequestRequestTypeDef",
    {
        "reference": ReferenceItemTypeDef,
        "name": str,
        "description": str,
        "tags": Mapping[str, str],
        "sseConfig": SseConfigTypeDef,
        "storeOptions": StoreOptionsTypeDef,
    },
    total=False,
)

class CreateAnnotationStoreRequestRequestTypeDef(
    _RequiredCreateAnnotationStoreRequestRequestTypeDef,
    _OptionalCreateAnnotationStoreRequestRequestTypeDef,
):
    pass

CreateAnnotationStoreResponseTypeDef = TypedDict(
    "CreateAnnotationStoreResponseTypeDef",
    {
        "id": str,
        "reference": ReferenceItemTypeDef,
        "storeFormat": StoreFormatType,
        "storeOptions": StoreOptionsTypeDef,
        "status": StoreStatusType,
        "name": str,
        "creationTime": datetime,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetAnnotationStoreResponseTypeDef = TypedDict(
    "GetAnnotationStoreResponseTypeDef",
    {
        "id": str,
        "reference": ReferenceItemTypeDef,
        "status": StoreStatusType,
        "storeArn": str,
        "name": str,
        "description": str,
        "sseConfig": SseConfigTypeDef,
        "creationTime": datetime,
        "updateTime": datetime,
        "tags": Dict[str, str],
        "storeOptions": StoreOptionsTypeDef,
        "storeFormat": StoreFormatType,
        "statusMessage": str,
        "storeSizeBytes": int,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

UpdateAnnotationStoreResponseTypeDef = TypedDict(
    "UpdateAnnotationStoreResponseTypeDef",
    {
        "id": str,
        "reference": ReferenceItemTypeDef,
        "status": StoreStatusType,
        "name": str,
        "description": str,
        "creationTime": datetime,
        "updateTime": datetime,
        "storeOptions": StoreOptionsTypeDef,
        "storeFormat": StoreFormatType,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetAnnotationImportResponseTypeDef = TypedDict(
    "GetAnnotationImportResponseTypeDef",
    {
        "id": str,
        "destinationName": str,
        "roleArn": str,
        "status": JobStatusType,
        "statusMessage": str,
        "creationTime": datetime,
        "updateTime": datetime,
        "completionTime": datetime,
        "items": List[AnnotationImportItemDetailTypeDef],
        "runLeftNormalization": bool,
        "formatOptions": FormatOptionsTypeDef,
        "annotationFields": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredStartAnnotationImportRequestRequestTypeDef = TypedDict(
    "_RequiredStartAnnotationImportRequestRequestTypeDef",
    {
        "destinationName": str,
        "roleArn": str,
        "items": Sequence[AnnotationImportItemSourceTypeDef],
    },
)
_OptionalStartAnnotationImportRequestRequestTypeDef = TypedDict(
    "_OptionalStartAnnotationImportRequestRequestTypeDef",
    {
        "formatOptions": FormatOptionsTypeDef,
        "runLeftNormalization": bool,
        "annotationFields": Mapping[str, str],
    },
    total=False,
)

class StartAnnotationImportRequestRequestTypeDef(
    _RequiredStartAnnotationImportRequestRequestTypeDef,
    _OptionalStartAnnotationImportRequestRequestTypeDef,
):
    pass
