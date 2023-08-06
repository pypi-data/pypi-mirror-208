import logging
import os
import time
import traceback
import typing as t

import pyarrow as pa
import pyarrow.parquet as pq
from sarus_data_spec import typing as st
from sarus_data_spec.constants import CACHE_PATH, TO_PARQUET_TASK
from sarus_data_spec.dataset import Dataset
from sarus_data_spec.manager.base import Base
from sarus_data_spec.manager.computations.local.base import LocalComputation
from sarus_data_spec.status import DataSpecErrorStatus, error, ready

from sarus.manager.arrow_remote import ToArrowComputationOnServer

logger = logging.getLogger(__name__)

BATCH_SIZE = 10000


class ToParquetComputation(LocalComputation[str]):
    """Class responsible for handling the caching
    in parquet of a dataset. It wraps a ToArrowComputation
    to get the iterator."""

    task_name = TO_PARQUET_TASK

    def __init__(
        self, computing_manager: Base, arrow_remote: ToArrowComputationOnServer
    ) -> None:
        super().__init__(computing_manager)
        self.remote_arrow = arrow_remote

    async def prepare(self, dataspec: st.DataSpec) -> None:
        logger.debug(f'STARTING LOCAL TO_PARQUET {dataspec.uuid()}')
        start = time.perf_counter()
        try:
            if self.computing_manager().is_computation_remote(dataspec):
                iterator = await self.remote_arrow.task_result(
                    dataspec, batch_size=BATCH_SIZE
                )
            else:
                iterator = await self.computing_manager().async_to_arrow_op(
                    dataset=t.cast(Dataset, dataspec), batch_size=BATCH_SIZE
                )

            batches = [batch async for batch in iterator]
            pq.write_table(
                table=pa.Table.from_batches(batches),
                where=self.cache_path(dataspec=dataspec),
                version='2.6',
            )
        except DataSpecErrorStatus as exception:
            error(
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
            error(
                dataspec=dataspec,
                manager=self.computing_manager(),
                task=self.task_name,
                properties={
                    "message": traceback.format_exc(),
                    'relaunch': str(False),
                },
            )
            raise DataSpecErrorStatus((False, traceback.format_exc()))
        else:
            end = time.perf_counter()
            logger.debug(
                f'FINISHED LOCAL TO_PARQUET {dataspec.uuid()} ({end-start:.2f}s)'
            )
            ready(
                dataspec=dataspec,
                manager=self.computing_manager(),
                task=TO_PARQUET_TASK,
                properties={CACHE_PATH: self.cache_path(dataspec)},
            )

    async def result_from_stage_properties(
        self,
        dataspec: st.DataSpec,
        properties: t.Mapping[str, str],
        **kwargs: t.Any,
    ) -> str:
        """Returns the cache_path"""
        return properties[CACHE_PATH]

    def cache_path(self, dataspec: st.DataSpec) -> str:
        """Returns the path where to cache the dataset"""
        return os.path.join(
            dataspec.manager().parquet_dir(), f"{dataspec.uuid()}.parquet"
        )
