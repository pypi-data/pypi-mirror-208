from enum import Enum
from typing import Any, Optional, Protocol, TypeVar, Union, runtime_checkable

import sarus_data_spec.context.typing as sct
import sarus_data_spec.typing as st
from requests import Session


class SyncPolicy(Enum):
    MANUAL = 0
    SEND_ON_INIT = 1
    SEND_ON_VALUE = 2


class DataSpecVariant(Enum):
    USER_DEFINED = "user_defined"
    SYNTHETIC = "synthetic"
    MOCK = "mock"
    ALTERNATIVE = "alternative"


T = TypeVar("T")


SPECIAL_WRAPPER_ATTRIBUTES = [
    "_alt_dataspec",
    "_dataspec",
    "_alt_policy",
    "_manager",
]

MOCK = "mock"
PYTHON_TYPE = "python_type"
ADMIN_DS = "admin_ds"
ATTRIBUTES_DS = "attributes_ds"


@runtime_checkable
class DataSpecWrapper(Protocol[T]):
    def python_type(self) -> Optional[str]:
        ...

    def dataspec(
        self, kind: DataSpecVariant = DataSpecVariant.USER_DEFINED
    ) -> st.DataSpec:
        ...

    def __sarus_eval__(
        self,
        target_epsilon: Optional[float] = None,
        verbose: Optional[int] = None,
    ) -> st.DataSpecValue:
        """Return value of synthetic variant."""
        ...


class DataSpecWrapperFactory(Protocol):
    def register(
        self,
        python_classname: str,
        sarus_wrapper_class: DataSpecWrapper,
    ) -> None:
        ...

    def create(self, dataspec: st.DataSpec) -> Union[DataSpecWrapper, Any]:
        """Create a wrapper class from a DataSpec.

        If the dataspec's python value is not managed by the SDK, returns an
        unwrapped Python object.
        """
        ...


class Client:
    def url(self) -> str:
        """Return the URL of the Sarus server."""

    def session(self) -> Session:
        """Return the connection to the server."""

    def context(self) -> sct.Context:
        """Return the client's context."""
