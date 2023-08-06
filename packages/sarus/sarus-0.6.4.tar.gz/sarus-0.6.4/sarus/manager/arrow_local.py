import logging
import time
import traceback
import typing as t

import pyarrow as pa
import pyarrow.parquet as pq
import sarus_data_spec.status as stt
from sarus_data_spec import typing as st
from sarus_data_spec.constants import ARROW_TASK
from sarus_data_spec.dataset import Dataset
from sarus_data_spec.manager.async_utils import async_iter
from sarus_data_spec.manager.base import Base
from sarus_data_spec.manager.computations.base import (
    ErrorCatchingAsyncIterator,
)
from sarus_data_spec.manager.computations.local.base import LocalComputation

from sarus.manager.arrow_remote import ToArrowComputationOnServer
from sarus.manager.parquet_local import ToParquetComputation

logger = logging.getLogger(__name__)


class ToArrowComputation(LocalComputation[t.AsyncIterator[pa.RecordBatch]]):
    task_name = ARROW_TASK

    def __init__(
        self,
        computing_manager: Base,
        parquet_computation: ToParquetComputation,
        arrow_remote: ToArrowComputationOnServer,
    ) -> None:
        super().__init__(computing_manager)
        self.parquet_computation = parquet_computation
        self.remote_arrow = arrow_remote

    async def prepare(self, dataspec: st.DataSpec) -> None:
        try:
            logger.debug(f'STARTED LOCAL ARROW {dataspec.uuid()}')
            start = time.perf_counter()
            # Only prepare parents since calling `to_arrow` will require the
            # computation of the scalars in the ancestry.
            dataset = t.cast(st.Dataset, dataspec)

            if self.computing_manager().is_cached(dataspec):
                await self.parquet_computation.complete_task(dataspec)

            elif self.computing_manager().is_computation_remote(dataspec):
                await self.arrow_remote.complete_task(dataspec)

            else:
                await self.computing_manager().async_prepare_parents(dataset)
                await self.computing_manager().async_schema(dataset)
        except stt.DataSpecErrorStatus as exception:
            stt.error(
                dataspec=dataspec,
                manager=self.computing_manager(),
                task=self.task_name,
                properties={
                    "message": traceback.format_exc(),
                    'relaunch': str(exception.relaunch),
                },
            )
            raise
        except Exception:
            stt.error(
                dataspec=dataspec,
                manager=self.computing_manager(),
                task=self.task_name,
                properties={
                    "message": traceback.format_exc(),
                    'relaunch': str(False),
                },
            )
            raise stt.DataSpecErrorStatus((False, traceback.format_exc()))
        else:
            end = time.perf_counter()
            logger.debug(
                f'FINISHED LOCAL ARROW {dataspec.uuid()} ({end-start:.2f}s)'
            )
            stt.ready(
                dataspec=dataspec,
                manager=self.computing_manager(),
                task=self.task_name,
            )

    async def result_from_stage_properties(
        self,
        dataspec: st.DataSpec,
        properties: t.Mapping[str, str],
        **kwargs: t.Any,
    ) -> t.AsyncIterator[pa.RecordBatch]:
        """Returns the iterator"""
        batch_size = kwargs['batch_size']

        if self.computing_manager().is_cached(dataspec):
            status = self.parquet_computation.status(dataspec)
            assert status
            stage = status.task(self.parquet_computation.task_name)
            assert stage
            assert stage.ready()
            cache_path = (
                await self.parquet_computation.result_from_stage_properties(
                    dataspec, stage.properties()
                )
            )
            try:
                ait = async_iter(
                    pq.read_table(source=cache_path).to_batches(
                        max_chunksize=batch_size
                    )
                )
            except Exception as e:
                stt.error(
                    dataspec=dataspec,
                    manager=self.computing_manager(),
                    task=self.task_name,
                    properties={
                        "message": traceback.format_exc(),
                        'relaunch': str(True),
                    },
                )
                stt.error(
                    dataspec=dataspec,
                    manager=self.computing_manager(),
                    task=self.parquet_computation.task_name,
                    properties={
                        "message": traceback.format_exc(),
                        'relaunch': str(True),
                    },
                )
                raise stt.DataSpecErrorStatus(
                    (True, traceback.format_exc())
                ) from e
        elif self.is_computation_remote(dataspec):
            status = self.remote_arrow.status(dataspec)
            ait = await self.remote_arrow.result_from_stage_properties(
                dataspec,
                batch_size=batch_size,
                properties=status.task(
                    self.remote_arrow.task_name
                ).properties(),
            )
        else:
            ait = await self.computing_manager().async_to_arrow_op(
                dataset=t.cast(Dataset, dataspec), batch_size=batch_size
            )
        return ErrorCatchingAsyncIterator(ait, dataspec, self)
