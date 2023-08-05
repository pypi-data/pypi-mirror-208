"""
Type annotations for omics service client waiters.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/)

Usage::

    ```python
    from boto3.session import Session

    from mypy_boto3_omics.client import OmicsClient
    from mypy_boto3_omics.waiter import (
        AnnotationImportJobCreatedWaiter,
        AnnotationStoreCreatedWaiter,
        AnnotationStoreDeletedWaiter,
        ReadSetActivationJobCompletedWaiter,
        ReadSetExportJobCompletedWaiter,
        ReadSetImportJobCompletedWaiter,
        ReferenceImportJobCompletedWaiter,
        RunCompletedWaiter,
        RunRunningWaiter,
        TaskCompletedWaiter,
        TaskRunningWaiter,
        VariantImportJobCreatedWaiter,
        VariantStoreCreatedWaiter,
        VariantStoreDeletedWaiter,
        WorkflowActiveWaiter,
    )

    session = Session()
    client: OmicsClient = session.client("omics")

    annotation_import_job_created_waiter: AnnotationImportJobCreatedWaiter = client.get_waiter("annotation_import_job_created")
    annotation_store_created_waiter: AnnotationStoreCreatedWaiter = client.get_waiter("annotation_store_created")
    annotation_store_deleted_waiter: AnnotationStoreDeletedWaiter = client.get_waiter("annotation_store_deleted")
    read_set_activation_job_completed_waiter: ReadSetActivationJobCompletedWaiter = client.get_waiter("read_set_activation_job_completed")
    read_set_export_job_completed_waiter: ReadSetExportJobCompletedWaiter = client.get_waiter("read_set_export_job_completed")
    read_set_import_job_completed_waiter: ReadSetImportJobCompletedWaiter = client.get_waiter("read_set_import_job_completed")
    reference_import_job_completed_waiter: ReferenceImportJobCompletedWaiter = client.get_waiter("reference_import_job_completed")
    run_completed_waiter: RunCompletedWaiter = client.get_waiter("run_completed")
    run_running_waiter: RunRunningWaiter = client.get_waiter("run_running")
    task_completed_waiter: TaskCompletedWaiter = client.get_waiter("task_completed")
    task_running_waiter: TaskRunningWaiter = client.get_waiter("task_running")
    variant_import_job_created_waiter: VariantImportJobCreatedWaiter = client.get_waiter("variant_import_job_created")
    variant_store_created_waiter: VariantStoreCreatedWaiter = client.get_waiter("variant_store_created")
    variant_store_deleted_waiter: VariantStoreDeletedWaiter = client.get_waiter("variant_store_deleted")
    workflow_active_waiter: WorkflowActiveWaiter = client.get_waiter("workflow_active")
    ```
"""
import sys
from typing import Sequence

from botocore.waiter import Waiter

from .literals import WorkflowTypeType
from .type_defs import WaiterConfigTypeDef

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "AnnotationImportJobCreatedWaiter",
    "AnnotationStoreCreatedWaiter",
    "AnnotationStoreDeletedWaiter",
    "ReadSetActivationJobCompletedWaiter",
    "ReadSetExportJobCompletedWaiter",
    "ReadSetImportJobCompletedWaiter",
    "ReferenceImportJobCompletedWaiter",
    "RunCompletedWaiter",
    "RunRunningWaiter",
    "TaskCompletedWaiter",
    "TaskRunningWaiter",
    "VariantImportJobCreatedWaiter",
    "VariantStoreCreatedWaiter",
    "VariantStoreDeletedWaiter",
    "WorkflowActiveWaiter",
)


class AnnotationImportJobCreatedWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.AnnotationImportJobCreated)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#annotationimportjobcreatedwaiter)
    """

    def wait(self, *, jobId: str, WaiterConfig: WaiterConfigTypeDef = ...) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.AnnotationImportJobCreated.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#annotationimportjobcreatedwaiter)
        """


class AnnotationStoreCreatedWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.AnnotationStoreCreated)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#annotationstorecreatedwaiter)
    """

    def wait(self, *, name: str, WaiterConfig: WaiterConfigTypeDef = ...) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.AnnotationStoreCreated.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#annotationstorecreatedwaiter)
        """


class AnnotationStoreDeletedWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.AnnotationStoreDeleted)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#annotationstoredeletedwaiter)
    """

    def wait(self, *, name: str, WaiterConfig: WaiterConfigTypeDef = ...) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.AnnotationStoreDeleted.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#annotationstoredeletedwaiter)
        """


class ReadSetActivationJobCompletedWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.ReadSetActivationJobCompleted)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#readsetactivationjobcompletedwaiter)
    """

    def wait(
        self, *, id: str, sequenceStoreId: str, WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.ReadSetActivationJobCompleted.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#readsetactivationjobcompletedwaiter)
        """


class ReadSetExportJobCompletedWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.ReadSetExportJobCompleted)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#readsetexportjobcompletedwaiter)
    """

    def wait(
        self, *, sequenceStoreId: str, id: str, WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.ReadSetExportJobCompleted.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#readsetexportjobcompletedwaiter)
        """


class ReadSetImportJobCompletedWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.ReadSetImportJobCompleted)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#readsetimportjobcompletedwaiter)
    """

    def wait(
        self, *, id: str, sequenceStoreId: str, WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.ReadSetImportJobCompleted.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#readsetimportjobcompletedwaiter)
        """


class ReferenceImportJobCompletedWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.ReferenceImportJobCompleted)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#referenceimportjobcompletedwaiter)
    """

    def wait(
        self, *, id: str, referenceStoreId: str, WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.ReferenceImportJobCompleted.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#referenceimportjobcompletedwaiter)
        """


class RunCompletedWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.RunCompleted)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#runcompletedwaiter)
    """

    def wait(
        self,
        *,
        id: str,
        export: Sequence[Literal["DEFINITION"]] = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.RunCompleted.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#runcompletedwaiter)
        """


class RunRunningWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.RunRunning)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#runrunningwaiter)
    """

    def wait(
        self,
        *,
        id: str,
        export: Sequence[Literal["DEFINITION"]] = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.RunRunning.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#runrunningwaiter)
        """


class TaskCompletedWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.TaskCompleted)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#taskcompletedwaiter)
    """

    def wait(self, *, id: str, taskId: str, WaiterConfig: WaiterConfigTypeDef = ...) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.TaskCompleted.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#taskcompletedwaiter)
        """


class TaskRunningWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.TaskRunning)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#taskrunningwaiter)
    """

    def wait(self, *, id: str, taskId: str, WaiterConfig: WaiterConfigTypeDef = ...) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.TaskRunning.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#taskrunningwaiter)
        """


class VariantImportJobCreatedWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.VariantImportJobCreated)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#variantimportjobcreatedwaiter)
    """

    def wait(self, *, jobId: str, WaiterConfig: WaiterConfigTypeDef = ...) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.VariantImportJobCreated.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#variantimportjobcreatedwaiter)
        """


class VariantStoreCreatedWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.VariantStoreCreated)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#variantstorecreatedwaiter)
    """

    def wait(self, *, name: str, WaiterConfig: WaiterConfigTypeDef = ...) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.VariantStoreCreated.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#variantstorecreatedwaiter)
        """


class VariantStoreDeletedWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.VariantStoreDeleted)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#variantstoredeletedwaiter)
    """

    def wait(self, *, name: str, WaiterConfig: WaiterConfigTypeDef = ...) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.VariantStoreDeleted.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#variantstoredeletedwaiter)
        """


class WorkflowActiveWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.WorkflowActive)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#workflowactivewaiter)
    """

    def wait(
        self,
        *,
        id: str,
        type: WorkflowTypeType = ...,
        export: Sequence[Literal["DEFINITION"]] = ...,
        WaiterConfig: WaiterConfigTypeDef = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics.html#Omics.Waiter.WorkflowActive.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_omics/waiters/#workflowactivewaiter)
        """
