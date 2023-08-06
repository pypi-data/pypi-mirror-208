from typing import cast

import sarus_data_spec.protobuf as sp
from sarus_data_spec.attribute import Attribute
from sarus_data_spec.context.public import Public as PublicContext
from sarus_data_spec.dataset import Dataset
from sarus_data_spec.factory import Factory
from sarus_data_spec.scalar import Scalar
from sarus_data_spec.schema import Schema

# from sarus.storage.local import Storage
from sarus_data_spec.storage.local import Storage
from sarus_data_spec.transform import Transform
from sarus_data_spec.variant_constraint import VariantConstraint

from sarus.dataspec_wrapper import MetaWrapper
from sarus.manager.sdk_manager import SDKManager, manager
from sarus.typing import Client
from sarus.wrapper_factory import DataSpecWrapperFactory

from ..typing import SyncPolicy


class LocalSDKContext(PublicContext):
    """A default context"""

    def __init__(self, client: Client, verbose: int = 1) -> None:
        super().__init__()
        self._storage = Storage()  # type:ignore
        self._sync_policy = SyncPolicy.SEND_ON_INIT
        self.client = client
        self._manager = manager(self.storage(), self.client)
        self._verbose = verbose

        self._dataspec_factory = Factory()
        self.factory().register(
            sp.type_name(sp.Dataset),
            lambda protobuf, store: Dataset(cast(sp.Dataset, protobuf), store),
        )
        self.factory().register(
            sp.type_name(sp.Scalar),
            lambda protobuf, store: Scalar(cast(sp.Scalar, protobuf), store),
        )
        self.factory().register(
            sp.type_name(sp.Transform),
            lambda protobuf, store: Transform(
                cast(sp.Transform, protobuf), store
            ),
        )
        self.factory().register(
            sp.type_name(sp.Schema),
            lambda protobuf, store: Schema(cast(sp.Schema, protobuf), store),
        )
        self.factory().register(
            sp.type_name(sp.Attribute),
            lambda protobuf, store: Attribute(
                cast(sp.Attribute, protobuf), store
            ),
        )

        self.factory().register(
            sp.type_name(sp.VariantConstraint),
            lambda protobuf, store: VariantConstraint(
                cast(sp.VariantConstraint, protobuf), store
            ),
        )

        self._wrapper_factory = DataSpecWrapperFactory()
        for (
            python_classname,
            sarus_wrapper_class,
        ) in MetaWrapper._wrapper_classes:
            self._wrapper_factory.register(
                python_classname=python_classname,
                sarus_wrapper_class=sarus_wrapper_class,
            )

    def verbose(self) -> int:
        return self._verbose

    def factory(self) -> Factory:
        return self._dataspec_factory

    def wrapper_factory(self) -> DataSpecWrapperFactory:
        return self._wrapper_factory

    def storage(self) -> Storage:
        return self._storage

    def manager(self) -> SDKManager:
        return self._manager

    def set_sync_policy(self, policy: SyncPolicy) -> None:
        self._sync_policy = policy

    def sync_policy(self) -> SyncPolicy:
        return self._sync_policy
