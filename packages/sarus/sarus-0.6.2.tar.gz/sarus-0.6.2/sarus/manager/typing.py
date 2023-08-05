import typing as t

import sarus_data_spec.typing as st
from sarus_data_spec.manager.base import Computation
from sarus_data_spec.manager.typing import Manager

from sarus.typing import Client


class SDKManager(Manager, t.Protocol):
    """The Manager of the SDK running on the client side.

    This Manager has two additional functionalities compared to the
    DelegatingManager manager.

    First, it manages the relationship with the remote server using the API
    endpoints.

    Second, this Manager defines a MOCK version for every DataSpec. The MOCK is
    defined as a smaller version of a DataSpec. In practice, it is a sample of
    SYNTHETIC at the source and MOCKs of transformed DataSpecs are the
    transforms of the MOCKs.

    The MOCK is created and its value computed in the `infer_output_type`
    method. This serves two purposes. First, it provides immediate feedback to
    the user in case of erroneous computation. Second, it allows identifying the
    MOCK's value Python type which is then used by the SDK to instantiate the
    correct DataSpecWrapper type (e.g. instantiate a sarus.pandas.DataFrame if
    the value is a pandas.DataFrame).
    """

    def python_type(self, dataspec: st.DataSpec) -> t.Optional[str]:
        """Return the Python class name of a DataSpec.

        This is used to instantiate the correct DataSpecWrapper class.
        """

    def client(self) -> Client:
        """Return the sarus.Client object used to make API calls."""

    def launch(self, dataspec: st.DataSpec) -> None:
        """Launch a Dataspec's computation on the server."""

    def compile(
        self, dataspec: st.DataSpec, target_epsilon: t.Optional[float] = None
    ) -> t.Tuple[st.DataSpec, str]:
        """Compile an alternative Dataspec on the server."""

    def push(self, dataspec: st.DataSpec) -> None:
        """Push a Dataspec's computation graph on the server."""

    def dataspec_computation(self, dataspec: st.DataSpec) -> Computation:
        """Return the Computation for getting the dataspec's value. If sql is
        is true, the sqlcomputation will be returned.
        """

    def set_admin_ds(
        self, source_ds: st.DataSpec, admin_ds: t.Dict[str, t.Any]
    ) -> None:
        """Attach the admin_ds to a source dataspec in a status."""

    def default_delta(self, dataspec: st.DataSpec) -> t.Optional[float]:
        """Get the default delta of a dataspec."""

    def consumed_epsilon(self, dataspec: st.DataSpec) -> float:
        """Get the consumed epsilon from the server."""
