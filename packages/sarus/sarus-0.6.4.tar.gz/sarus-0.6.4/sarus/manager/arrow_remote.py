import typing as t

import pyarrow as pa
import sarus_data_spec.status as stt
from sarus_data_spec import typing as st
from sarus_data_spec.constants import ARROW_TASK
from sarus_data_spec.manager.computations.base import (
    ErrorCatchingAsyncIterator,
)

from sarus.manager.base_remote import RemoteComputation

from .dataspec_api import dataset_result, dataspec_status, launch_dataspec


class ToArrowComputationOnServer(
    RemoteComputation[t.AsyncIterator[pa.RecordBatch]]
):
    """ToArrowComputation on the Sarus server through the REST API."""

    task_name = ARROW_TASK

    def launch_task(self, dataspec: st.DataSpec) -> None:
        """Launch the computation of a Dataset on the server."""
        status = self.status(dataspec)
        if status is None:
            launch_dataspec(self.computing_manager().client(), dataspec.uuid())

    async def result_from_stage_properties(
        self,
        dataspec: st.DataSpec,
        properties: t.Mapping[str, str],
        **kwargs: t.Any,
    ) -> t.AsyncIterator[pa.RecordBatch]:
        """Return the task result, launch the computation if needed."""
        batch_size = kwargs["batch_size"]
        ait = dataset_result(
            self.computing_manager().client(), dataspec.uuid(), batch_size
        )
        return ErrorCatchingAsyncIterator(ait, dataspec, self)

    def status(self, dataspec: st.DataSpec) -> t.Optional[st.Status]:
        """In this case, the computation retrieves the status from the server
        via an API call, a local status is created but not stored in order
        to use it just for the polling"""

        status_proto = dataspec_status(
            client=self.computing_manager().client(),
            uuid=dataspec.uuid(),
            task_names=[self.task_name],
        )
        if status_proto is None:
            return None
        else:
            return stt.Status(protobuf=status_proto, store=False)
