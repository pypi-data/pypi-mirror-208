import sarus_data_spec.status as stt
from sarus_data_spec import typing as st
from sarus_data_spec.manager.computations.base import status_error_policy
from sarus_data_spec.manager.computations.remote.base import (
    RemoteComputation as BaseRemote,
)
from sarus_data_spec.manager.computations.remote.base import T

from .dataspec_api import launch_dataspec


class RemoteComputation(BaseRemote[T]):
    async def error(
        self,
        dataspec: st.DataSpec,
    ) -> st.Status:
        """For Remote computations, when mthere is an error status
        to be relaunched, a new api call is done"""
        status = self.status(dataspec)
        if status is not None:
            stage = status.task(self.task_name)
            assert stage
            should_clear = status_error_policy(stage=stage)
            if should_clear:
                launch_dataspec(
                    self.computing_manager().client(), dataspec.uuid()
                )
                return await self.complete_task(dataspec=dataspec)
            raise stt.DataSpecErrorStatus(
                (
                    stage.properties()["relaunch"] == str(True),
                    stage.properties()["message"],
                )
            )
        return await self.complete_task(dataspec=dataspec)
