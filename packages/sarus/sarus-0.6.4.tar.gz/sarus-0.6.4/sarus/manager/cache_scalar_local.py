import logging
import os
import pickle as pkl
import time
import traceback
import typing as t

import sarus_data_spec.protobuf as sp
from sarus_data_spec import typing as st
from sarus_data_spec.constants import (
    CACHE_PATH,
    CACHE_PROTO,
    CACHE_SCALAR_TASK,
    CACHE_TYPE,
    ScalarCaching,
)
from sarus_data_spec.manager.base import Base
from sarus_data_spec.manager.computations.local.base import LocalComputation
from sarus_data_spec.scalar import Scalar
from sarus_data_spec.status import DataSpecErrorStatus, error, ready

from sarus.manager.value_remote import ValueComputationOnServer

logger = logging.getLogger(__name__)


class CacheScalarComputation(LocalComputation[t.Tuple[str, str]]):
    """Class responsible for handling the caching
    in of a scalar. It wraps a ValueComputation to get the value."""

    task_name = CACHE_SCALAR_TASK

    def __init__(
        self, computing_manager: Base, remote_scalar: ValueComputationOnServer
    ) -> None:
        super().__init__(computing_manager)
        self.remote_scalar = remote_scalar

    async def prepare(self, dataspec: st.DataSpec) -> None:
        logger.debug(f'STARTING CACHE_SCALAR {dataspec.uuid()}')
        start = time.perf_counter()
        try:
            if self.computing_manager().is_computation_remote(dataspec):
                value = await self.remote_scalar.task_result(dataspec)
            else:
                value = await self.computing_manager().async_value_op(
                    scalar=t.cast(Scalar, dataspec)
                )

            if isinstance(value, st.HasProtobuf):
                properties = {
                    CACHE_PROTO: sp.to_base64(value.protobuf()),
                    CACHE_TYPE: sp.type_name(value.prototype()),
                }
            else:
                properties = {
                    CACHE_TYPE: ScalarCaching.PICKLE.value,
                    CACHE_PATH: self.cache_path(dataspec),
                }
                with open(self.cache_path(dataspec), "wb") as f:
                    pkl.dump(value, f)

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
                f'FINISHED CACHE_SCALAR {dataspec.uuid()} ({end-start:.2f}s)'
            )
            ready(
                dataspec=dataspec,
                manager=self.computing_manager(),
                task=self.task_name,
                properties=properties,
            )

    async def result_from_stage_properties(
        self,
        dataspec: st.DataSpec,
        properties: t.Mapping[str, str],
        **kwargs: t.Any,
    ) -> t.Tuple[str, str]:
        """Reads the cache and returns the value."""
        if properties[CACHE_TYPE] == ScalarCaching.PICKLE.value:
            return properties[CACHE_TYPE], properties[CACHE_PATH]
        return properties[CACHE_TYPE], properties[CACHE_PROTO]

    def cache_path(self, dataspec: st.DataSpec) -> str:
        """Returns the path where to cache the scalar."""
        return os.path.join(
            dataspec.manager().parquet_dir(), f"{dataspec.uuid()}.pkl"
        )
