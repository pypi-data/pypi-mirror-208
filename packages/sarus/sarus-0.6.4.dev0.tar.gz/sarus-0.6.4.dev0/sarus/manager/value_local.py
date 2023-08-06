import logging
import pickle as pkl
import time
import traceback
import typing as t

import sarus_data_spec.protobuf as sp
import sarus_data_spec.status as stt
from sarus_data_spec import typing as st
from sarus_data_spec.constants import SCALAR_TASK, ScalarCaching
from sarus_data_spec.manager.base import Base
from sarus_data_spec.manager.computations.local.base import LocalComputation
from sarus_data_spec.scalar import Scalar

from sarus.manager.cache_scalar_local import CacheScalarComputation
from sarus.manager.value_remote import ValueComputationOnServer

logger = logging.getLogger(__name__)


class ValueComputation(LocalComputation[t.Any]):
    """Class responsible for handling the computation
    of scalars."""

    task_name = SCALAR_TASK

    def __init__(
        self,
        computing_manager: Base,
        cache_scalar_computation: CacheScalarComputation,
        remote_scalar: ValueComputationOnServer,
    ) -> None:
        super().__init__(computing_manager)
        self.cache_scalar_computation = cache_scalar_computation
        self.remote_scalar = remote_scalar

    async def result_from_stage_properties(
        self,
        dataspec: st.DataSpec,
        properties: t.Mapping[str, str],
        **kwargs: t.Any,
    ) -> t.Any:
        if self.computing_manager().is_cached(dataspec):
            (
                cache_type,
                cache,
            ) = await self.cache_scalar_computation.task_result(dataspec)
            try:
                if cache_type == ScalarCaching.PICKLE.value:
                    with open(cache, "rb") as f:
                        data = pkl.load(f)

                else:
                    data = sp.python_proto_factory(cache, cache_type)
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
                    task=self.cache_scalar_computation.task_name,
                    properties={
                        "message": traceback.format_exc(),
                        'relaunch': str(True),
                    },
                )
                raise stt.DataSpecErrorStatus(
                    (True, traceback.format_exc())
                ) from e
            else:
                return data

        if self.computing_manager().is_computation_remote(dataspec):
            status = self.remote_scalar.status(dataspec)
            return await self.remote_scalar.result_from_stage_properties(
                dataspec, properties=status.task(self.task_name).properties()
            )

        return await self.computing_manager().async_value_op(
            scalar=t.cast(Scalar, dataspec)
        )

    async def prepare(self, dataspec: st.DataSpec) -> None:
        try:
            logger.debug(f'STARTED LOCAL SCALAR {dataspec.uuid()}')
            start = time.perf_counter()
            if self.computing_manager().is_cached(dataspec):
                await self.cache_scalar_computation.task_result(dataspec)

            elif self.computing_manager().is_computation_remote(dataspec):
                await self.remote_scalar.complete_task(dataspec)
            else:
                await self.computing_manager().async_prepare_parents(dataspec)
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
            logging.debug(
                f'FINISHED LOCAL SCALAR {dataspec.uuid()} ({end-start:.2f}s)'
            )
            stt.ready(
                dataspec=dataspec,
                manager=self.computing_manager(),
                task=self.task_name,
            )
