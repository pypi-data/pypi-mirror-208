"""
Type annotations for omics service client paginators.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/)

Usage::

    ```python
    from boto3.session import Session

    from mypy_boto3_omics.client import OmicsClient
    from mypy_boto3_omics.paginator import (
        ListAnnotationImportJobsPaginator,
        ListAnnotationStoresPaginator,
        ListMultipartReadSetUploadsPaginator,
        ListReadSetActivationJobsPaginator,
        ListReadSetExportJobsPaginator,
        ListReadSetImportJobsPaginator,
        ListReadSetUploadPartsPaginator,
        ListReadSetsPaginator,
        ListReferenceImportJobsPaginator,
        ListReferenceStoresPaginator,
        ListReferencesPaginator,
        ListRunGroupsPaginator,
        ListRunTasksPaginator,
        ListRunsPaginator,
        ListSequenceStoresPaginator,
        ListVariantImportJobsPaginator,
        ListVariantStoresPaginator,
        ListWorkflowsPaginator,
    )

    session = Session()
    client: OmicsClient = session.client("omics")

    list_annotation_import_jobs_paginator: ListAnnotationImportJobsPaginator = client.get_paginator("list_annotation_import_jobs")
    list_annotation_stores_paginator: ListAnnotationStoresPaginator = client.get_paginator("list_annotation_stores")
    list_multipart_read_set_uploads_paginator: ListMultipartReadSetUploadsPaginator = client.get_paginator("list_multipart_read_set_uploads")
    list_read_set_activation_jobs_paginator: ListReadSetActivationJobsPaginator = client.get_paginator("list_read_set_activation_jobs")
    list_read_set_export_jobs_paginator: ListReadSetExportJobsPaginator = client.get_paginator("list_read_set_export_jobs")
    list_read_set_import_jobs_paginator: ListReadSetImportJobsPaginator = client.get_paginator("list_read_set_import_jobs")
    list_read_set_upload_parts_paginator: ListReadSetUploadPartsPaginator = client.get_paginator("list_read_set_upload_parts")
    list_read_sets_paginator: ListReadSetsPaginator = client.get_paginator("list_read_sets")
    list_reference_import_jobs_paginator: ListReferenceImportJobsPaginator = client.get_paginator("list_reference_import_jobs")
    list_reference_stores_paginator: ListReferenceStoresPaginator = client.get_paginator("list_reference_stores")
    list_references_paginator: ListReferencesPaginator = client.get_paginator("list_references")
    list_run_groups_paginator: ListRunGroupsPaginator = client.get_paginator("list_run_groups")
    list_run_tasks_paginator: ListRunTasksPaginator = client.get_paginator("list_run_tasks")
    list_runs_paginator: ListRunsPaginator = client.get_paginator("list_runs")
    list_sequence_stores_paginator: ListSequenceStoresPaginator = client.get_paginator("list_sequence_stores")
    list_variant_import_jobs_paginator: ListVariantImportJobsPaginator = client.get_paginator("list_variant_import_jobs")
    list_variant_stores_paginator: ListVariantStoresPaginator = client.get_paginator("list_variant_stores")
    list_workflows_paginator: ListWorkflowsPaginator = client.get_paginator("list_workflows")
    ```
"""
from typing import Generic, Iterator, Sequence, TypeVar

from botocore.paginate import PageIterator, Paginator

from .literals import ReadSetPartSourceType, RunStatusType, TaskStatusType, WorkflowTypeType
from .type_defs import (
    ActivateReadSetFilterTypeDef,
    ExportReadSetFilterTypeDef,
    ImportReadSetFilterTypeDef,
    ImportReferenceFilterTypeDef,
    ListAnnotationImportJobsFilterTypeDef,
    ListAnnotationImportJobsResponseTypeDef,
    ListAnnotationStoresFilterTypeDef,
    ListAnnotationStoresResponseTypeDef,
    ListMultipartReadSetUploadsResponseTypeDef,
    ListReadSetActivationJobsResponseTypeDef,
    ListReadSetExportJobsResponseTypeDef,
    ListReadSetImportJobsResponseTypeDef,
    ListReadSetsResponseTypeDef,
    ListReadSetUploadPartsResponseTypeDef,
    ListReferenceImportJobsResponseTypeDef,
    ListReferencesResponseTypeDef,
    ListReferenceStoresResponseTypeDef,
    ListRunGroupsResponseTypeDef,
    ListRunsResponseTypeDef,
    ListRunTasksResponseTypeDef,
    ListSequenceStoresResponseTypeDef,
    ListVariantImportJobsFilterTypeDef,
    ListVariantImportJobsResponseTypeDef,
    ListVariantStoresFilterTypeDef,
    ListVariantStoresResponseTypeDef,
    ListWorkflowsResponseTypeDef,
    PaginatorConfigTypeDef,
    ReadSetFilterTypeDef,
    ReadSetUploadPartListFilterTypeDef,
    ReferenceFilterTypeDef,
    ReferenceStoreFilterTypeDef,
    SequenceStoreFilterTypeDef,
)

__all__ = (
    "ListAnnotationImportJobsPaginator",
    "ListAnnotationStoresPaginator",
    "ListMultipartReadSetUploadsPaginator",
    "ListReadSetActivationJobsPaginator",
    "ListReadSetExportJobsPaginator",
    "ListReadSetImportJobsPaginator",
    "ListReadSetUploadPartsPaginator",
    "ListReadSetsPaginator",
    "ListReferenceImportJobsPaginator",
    "ListReferenceStoresPaginator",
    "ListReferencesPaginator",
    "ListRunGroupsPaginator",
    "ListRunTasksPaginator",
    "ListRunsPaginator",
    "ListSequenceStoresPaginator",
    "ListVariantImportJobsPaginator",
    "ListVariantStoresPaginator",
    "ListWorkflowsPaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListAnnotationImportJobsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListAnnotationImportJobs)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listannotationimportjobspaginator)
    """

    def paginate(
        self,
        *,
        ids: Sequence[str] = ...,
        filter: ListAnnotationImportJobsFilterTypeDef = ...,
        PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListAnnotationImportJobsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListAnnotationImportJobs.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listannotationimportjobspaginator)
        """


class ListAnnotationStoresPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListAnnotationStores)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listannotationstorespaginator)
    """

    def paginate(
        self,
        *,
        ids: Sequence[str] = ...,
        filter: ListAnnotationStoresFilterTypeDef = ...,
        PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListAnnotationStoresResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListAnnotationStores.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listannotationstorespaginator)
        """


class ListMultipartReadSetUploadsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListMultipartReadSetUploads)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listmultipartreadsetuploadspaginator)
    """

    def paginate(
        self, *, sequenceStoreId: str, PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListMultipartReadSetUploadsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListMultipartReadSetUploads.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listmultipartreadsetuploadspaginator)
        """


class ListReadSetActivationJobsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListReadSetActivationJobs)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listreadsetactivationjobspaginator)
    """

    def paginate(
        self,
        *,
        sequenceStoreId: str,
        filter: ActivateReadSetFilterTypeDef = ...,
        PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListReadSetActivationJobsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListReadSetActivationJobs.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listreadsetactivationjobspaginator)
        """


class ListReadSetExportJobsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListReadSetExportJobs)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listreadsetexportjobspaginator)
    """

    def paginate(
        self,
        *,
        sequenceStoreId: str,
        filter: ExportReadSetFilterTypeDef = ...,
        PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListReadSetExportJobsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListReadSetExportJobs.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listreadsetexportjobspaginator)
        """


class ListReadSetImportJobsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListReadSetImportJobs)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listreadsetimportjobspaginator)
    """

    def paginate(
        self,
        *,
        sequenceStoreId: str,
        filter: ImportReadSetFilterTypeDef = ...,
        PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListReadSetImportJobsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListReadSetImportJobs.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listreadsetimportjobspaginator)
        """


class ListReadSetUploadPartsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListReadSetUploadParts)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listreadsetuploadpartspaginator)
    """

    def paginate(
        self,
        *,
        sequenceStoreId: str,
        uploadId: str,
        partSource: ReadSetPartSourceType,
        filter: ReadSetUploadPartListFilterTypeDef = ...,
        PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListReadSetUploadPartsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListReadSetUploadParts.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listreadsetuploadpartspaginator)
        """


class ListReadSetsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListReadSets)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listreadsetspaginator)
    """

    def paginate(
        self,
        *,
        sequenceStoreId: str,
        filter: ReadSetFilterTypeDef = ...,
        PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListReadSetsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListReadSets.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listreadsetspaginator)
        """


class ListReferenceImportJobsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListReferenceImportJobs)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listreferenceimportjobspaginator)
    """

    def paginate(
        self,
        *,
        referenceStoreId: str,
        filter: ImportReferenceFilterTypeDef = ...,
        PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListReferenceImportJobsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListReferenceImportJobs.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listreferenceimportjobspaginator)
        """


class ListReferenceStoresPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListReferenceStores)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listreferencestorespaginator)
    """

    def paginate(
        self,
        *,
        filter: ReferenceStoreFilterTypeDef = ...,
        PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListReferenceStoresResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListReferenceStores.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listreferencestorespaginator)
        """


class ListReferencesPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListReferences)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listreferencespaginator)
    """

    def paginate(
        self,
        *,
        referenceStoreId: str,
        filter: ReferenceFilterTypeDef = ...,
        PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListReferencesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListReferences.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listreferencespaginator)
        """


class ListRunGroupsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListRunGroups)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listrungroupspaginator)
    """

    def paginate(
        self, *, name: str = ..., PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListRunGroupsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListRunGroups.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listrungroupspaginator)
        """


class ListRunTasksPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListRunTasks)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listruntaskspaginator)
    """

    def paginate(
        self,
        *,
        id: str,
        status: TaskStatusType = ...,
        PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListRunTasksResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListRunTasks.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listruntaskspaginator)
        """


class ListRunsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListRuns)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listrunspaginator)
    """

    def paginate(
        self,
        *,
        name: str = ...,
        runGroupId: str = ...,
        status: RunStatusType = ...,
        PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListRunsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListRuns.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listrunspaginator)
        """


class ListSequenceStoresPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListSequenceStores)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listsequencestorespaginator)
    """

    def paginate(
        self,
        *,
        filter: SequenceStoreFilterTypeDef = ...,
        PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListSequenceStoresResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListSequenceStores.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listsequencestorespaginator)
        """


class ListVariantImportJobsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListVariantImportJobs)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listvariantimportjobspaginator)
    """

    def paginate(
        self,
        *,
        ids: Sequence[str] = ...,
        filter: ListVariantImportJobsFilterTypeDef = ...,
        PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListVariantImportJobsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListVariantImportJobs.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listvariantimportjobspaginator)
        """


class ListVariantStoresPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListVariantStores)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listvariantstorespaginator)
    """

    def paginate(
        self,
        *,
        ids: Sequence[str] = ...,
        filter: ListVariantStoresFilterTypeDef = ...,
        PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListVariantStoresResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListVariantStores.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listvariantstorespaginator)
        """


class ListWorkflowsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListWorkflows)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listworkflowspaginator)
    """

    def paginate(
        self,
        *,
        type: WorkflowTypeType = ...,
        name: str = ...,
        PaginationConfig: "PaginatorConfigTypeDef" = ...
    ) -> _PageIterator[ListWorkflowsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Paginator.ListWorkflows.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/paginators/#listworkflowspaginator)
        """
