import json
import os
import tempfile
import typing as t

import pyarrow as pa
import requests
import sarus_data_spec.protobuf as sp
import sarus_data_spec.status as stt
import sarus_data_spec.storage.typing as storage_typing
import sarus_data_spec.type as sdt
import sarus_data_spec.typing as st
from sarus_data_spec.arrow.type import type_from_arrow
from sarus_data_spec.attribute import attach_properties
from sarus_data_spec.constants import (
    ARROW_TASK,
    BIG_DATA_TASK,
    IS_BIG_DATA,
    SCALAR_TASK,
)
from sarus_data_spec.dataspec_validator.privacy_limit import DeltaEpsilonLimit
from sarus_data_spec.dataspec_validator.typing import DataspecPrivacyPolicy
from sarus_data_spec.manager.base import Base
from sarus_data_spec.manager.computations.base import BaseComputation
from sarus_data_spec.manager.computations.local.schema import SchemaComputation
from sarus_data_spec.manager.ops.processor.routing import (
    TransformedDataset,
    TransformedScalar,
)
from sarus_data_spec.manager.ops.source.routing import SourceScalar
from sarus_data_spec.schema import schema as schema_builder

import sarus.manager.dataspec_api as api
import sarus.manager.ops.api as api_ops
from sarus.typing import ADMIN_DS, MOCK, PYTHON_TYPE, Client

from .arrow_local import ToArrowComputation
from .arrow_remote import ToArrowComputationOnServer
from .cache_scalar_local import CacheScalarComputation
from .parquet_local import ToParquetComputation
from .value_local import ValueComputation
from .value_remote import ValueComputationOnServer


class SDKManager(Base):
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

    def __init__(
        self,
        storage: storage_typing.Storage,
        protobuf: sp.Manager,
        client: Client,
    ) -> None:
        super().__init__(storage, protobuf)

        self.schema_computation = SchemaComputation(self)
        self.to_parquet_computation = ToParquetComputation(
            self, arrow_remote=ToArrowComputationOnServer(self)
        )
        self.to_arrow_computation = ToArrowComputation(
            self,
            parquet_computation=self.to_parquet_computation,
            arrow_remote=self.to_parquet_computation.remote_arrow,
        )
        self.cache_scalar_computation = CacheScalarComputation(
            self, ValueComputationOnServer(self)
        )
        self.value_computation = ValueComputation(
            self,
            cache_scalar_computation=self.cache_scalar_computation,
            remote_scalar=self.cache_scalar_computation.remote_scalar,
        )

        self._client = client
        self._mock_size = 1000
        self._parquet_dir = os.path.join(tempfile.mkdtemp(), "sarus_dataspec")
        os.makedirs(self._parquet_dir, exist_ok=True)

    def set_admin_ds(
        self, source_ds: st.DataSpec, admin_ds: t.Dict[str, t.Any]
    ) -> None:
        """Attach the admin_ds to a source dataspec in a status."""
        assert source_ds.is_source()
        if source_ds.status([ADMIN_DS]) is None:
            stt.ready(
                source_ds,
                task=ADMIN_DS,
                properties={ADMIN_DS: json.dumps(admin_ds)},
            )

    def default_delta(self, dataspec: st.DataSpec) -> t.Optional[float]:
        """Get the default delta of a dataspec."""
        sources_ds = dataspec.sources(sp.type_name(sp.Dataset))
        source = sources_ds.pop()
        status = source.status(task_names=[ADMIN_DS])
        if status is None:
            return None
        stage = status.task(task=ADMIN_DS)
        assert stage.ready()
        admin_ds = json.loads(stage[ADMIN_DS])
        # TODO : revise this when the API provides a unified endpoint for
        # applied access rule
        delta = admin_ds.get("accesses").pop(0).get("delta")
        return float(delta)

    def consumed_epsilon(self, dataspec: st.DataSpec) -> float:
        """Get the consumed epsilon from the server."""
        # TODO works only when the value is already computed on the server side
        _, epsilon = api.get_dataspec(self.client(), dataspec.uuid())
        return epsilon

    def client(self) -> Client:
        """Return the sarus.Client object used to make API calls."""
        return self._client

    def is_cached(self, dataspec: st.DataSpec) -> bool:
        """Return True if the dataspec is cached locally."""
        return True

    def is_computation_remote(self, dataspec: st.DataSpec) -> bool:
        """Return True if the dataspec is remotely computed."""
        # `select_sql` transforms are delegated, whether mock or not
        if dataspec.is_transformed():
            transform = dataspec.transform()
            if transform.protobuf().spec.HasField("select_sql"):
                computation_graph = self.computation_graph(dataspec)
                referrables = (
                    list(computation_graph["dataspecs"])
                    + list(computation_graph["transforms"])
                    + list(computation_graph["attributes"])
                )
                api.push_dataspec_graph(self._client, referrables)

        ds, _ = api.get_dataspec(self.client(), dataspec.uuid())
        return ds is not None

    def is_big_data(self, dataset: st.Dataset) -> bool:
        """Method to compute is_big data if the status
        is not in the storage and the dataset is source
        we retrieve it via an api call"""

        last_status = self.status(dataset, task_name=BIG_DATA_TASK)
        if last_status:
            stage = last_status.task(task=BIG_DATA_TASK)
            is_big = stage.properties().get(IS_BIG_DATA)
            return is_big == str(True)

        if dataset.is_source():
            status_proto = api.dataspec_status(
                self.client(), dataset.uuid(), task_names=[BIG_DATA_TASK]
            )
            stt.ready(
                dataset,
                manager=self,
                task=BIG_DATA_TASK,
                properties=status_proto.task_stages[BIG_DATA_TASK].properties,
            )
            return status_proto.task_stages[BIG_DATA_TASK].properties[
                IS_BIG_DATA
            ] == str(True)
        return super().is_big_data(dataset)

    def push(self, dataspec: st.DataSpec) -> None:
        """Push a Dataspec's computation graph on the server."""
        computation_graph = self.computation_graph(dataspec)
        referrables = (
            list(computation_graph["dataspecs"])
            + list(computation_graph["transforms"])
            + list(computation_graph["attributes"])
        )
        api.push_dataspec_graph(self.client(), referrables)

    def compile(
        self, dataspec: st.DataSpec, target_epsilon: t.Optional[float] = None
    ) -> t.Tuple[st.DataSpec, DataspecPrivacyPolicy]:
        """Compile an alternative Dataspec."""
        if target_epsilon is not None:
            default_delta = self.default_delta(dataspec)
            if default_delta is None:
                raise ValueError(f"Default delta not defined for {dataspec}")
            privacy_limit = DeltaEpsilonLimit({default_delta: target_epsilon})
        else:
            privacy_limit = None

        alt_dataspec_uuid, privacy_policy = api.compile_dataspec(
            self.client(), dataspec.uuid(), privacy_limit=privacy_limit
        )
        api.pull_dataspec_graph(self.client(), alt_dataspec_uuid)
        alt_dataspec = self.storage().referrable(alt_dataspec_uuid)
        return alt_dataspec, privacy_policy

    def launch(self, dataspec: st.DataSpec) -> None:
        """Launch a Dataspec's computation on the server."""
        api.launch_dataspec(self.client(), dataspec.uuid())

    def python_type(self, dataspec: st.DataSpec) -> str:
        """Return the Python class name of a DataSpec.

        This is used to instantiate the correct DataSpecWrapper class.
        """
        python_type_att = dataspec.attribute(name=PYTHON_TYPE)
        if python_type_att is not None:
            return python_type_att.properties().get(PYTHON_TYPE)

        if not dataspec.is_transformed():
            return str(t.Iterator[pa.RecordBatch])

        transform = dataspec.transform()
        if not transform.is_external():
            type_str = str(t.Iterator[pa.RecordBatch])
        else:
            ds_args, ds_kwargs = dataspec.parents()
            mock_value = self.mock_value(transform, *ds_args, **ds_kwargs)
            type_str = str(type(mock_value))

        attach_properties(
            dataspec, name=PYTHON_TYPE, properties={PYTHON_TYPE: type_str}
        )
        return type_str

    Edge = t.Tuple[st.DataSpec, st.DataSpec, st.Transform]

    def computation_graph(
        self, dataspec: st.DataSpec
    ) -> t.Dict[str, t.Union[st.DataSpec, st.Transform, st.Attribute, Edge]]:
        """Retreive all items necessary to compute a DataSpec.

        This function is used intensively to post DataSpecs, draw dot
        representationss, fetch statuses, and so on.
        """
        storage = self.storage()

        class ComputationGraphVisitor(st.Visitor):
            dataspecs: t.List[st.DataSpec] = list()
            transforms: t.Set[st.Transform] = set()
            edges: t.Set[
                t.Tuple[st.DataSpec, st.DataSpec, st.Transform]
            ] = set()
            attributes: t.Set[st.Attribute] = set()
            variant_constraints: t.Set[st.VariantConstraint] = set()
            graph: t.Dict[str, t.Set[str]] = dict()

            def transformed(
                self,
                visited: st.DataSpec,
                transform: st.Transform,
                *arguments: st.DataSpec,
                **named_arguments: st.DataSpec,
            ) -> None:
                if visited not in self.dataspecs:
                    self.dataspecs.append(visited)

                    attributes: t.List[st.Attribute] = storage.referring(
                        visited, type_name=sp.type_name(sp.Attribute)
                    )
                    # Don't send MOCK and PYTHON_TYPE attributes to the server
                    self.attributes.update(
                        [
                            att
                            for att in attributes
                            if att.name() not in [MOCK, PYTHON_TYPE]
                        ]
                    )

                    variant_constraints = storage.referring(
                        visited, type_name=sp.type_name(sp.VariantConstraint)
                    )
                    self.variant_constraints.update(
                        [vc for vc in variant_constraints]
                    )

                    self.transforms.add(transform)
                    for argument in arguments:
                        argument.accept(self)
                        self.edges.add((argument, visited, transform))
                    for _, argument in named_arguments.items():
                        argument.accept(self)
                        self.edges.add((argument, visited, transform))

            def other(self, visited: st.DataSpec) -> None:
                if visited not in self.dataspecs:
                    self.dataspecs.append(visited)

        visitor = ComputationGraphVisitor()
        dataspec.accept(visitor)

        return {
            "dataspecs": visitor.dataspecs[::-1],
            "transforms": visitor.transforms,
            "attributes": visitor.attributes,
            "variant_constraints": visitor.variant_constraints,
            "edges": visitor.edges,
        }

    def _delete_remote(self, uuid: str) -> requests.Response:
        """Delete a DataSpec and referring items on the server."""
        return api_ops.delete_dataspec(client=self.client(), uuid=uuid)

    def _delete_local(self, uuid: str) -> None:
        """Delete a DataSpec locally. MOCKs also have to be deleted."""
        would_delete = self.storage().all_referrings(uuid)
        additional_cleanup = []
        for uuid in would_delete:
            item = self.storage().referrable(uuid)
            if item.prototype() in [sp.Dataset, sp.Scalar]:
                try:
                    mock = item.variant(st.ConstraintKind.MOCK)
                except Exception:
                    pass
                else:
                    if mock:
                        additional_cleanup.append(mock)

        self.storage().delete(uuid)
        for item in additional_cleanup:
            self.storage().delete(item.uuid())

    def dot(
        self,
        dataspec: st.DataSpec,
        symbols: t.Dict[str, t.Optional[str]] = dict(),
        remote: bool = True,
        task_names: t.List[str] = [ARROW_TASK, SCALAR_TASK],
    ) -> str:
        """Graphviz dot language representation of the graph.

        Statuses are represented with a color code. The symbols are the
        caller's symbol for the DataSpec wrapper
        (see DataSpecWrapper.dataspec_wrapper_symbols).
        """
        graph = self.computation_graph(dataspec)
        dataspecs = graph["dataspecs"]
        TASK = (
            ARROW_TASK if dataspec.prototype() == sp.Dataset else SCALAR_TASK
        )

        # Get statuses wether remote or local
        if remote:
            statuses_proto = api.pull_dataspec_status_graph(
                self._client, dataspec.uuid(), task_names
            )
            statuses = {
                proto.dataspec: stt.Status(proto, store=False)
                for proto in statuses_proto
            }
        else:
            statuses = {
                ds.uuid(): stt.last_status(ds, task=TASK) for ds in dataspecs
            }

        edges, nodes, props = [], [], []
        for dataspec in dataspecs:
            status = statuses.get(dataspec.uuid())
            nodes.append(self.node_repr(dataspec, status, symbols))
        for parent, child, transform in graph["edges"]:
            edges.append(
                f'"{parent.uuid()}" -> "{child.uuid()}"'
                f'[label="{transform.name()}"];'
            )
        props = [
            'node [style="rounded,filled"]',
        ]
        dot = ["digraph {"] + props + nodes + edges + ["}"]
        return "\n".join(dot)

    def node_repr(
        self,
        dataspec: st.DataSpec,
        status: t.Optional[st.Status],
        symbols: t.Dict[str, t.Optional[str]],
    ) -> str:
        """Style a graph node depending on its status and symbol."""
        shape = "box"
        FILLCOLORS = {
            "error": "#ff9c9c",
            "ready": "#9cffc5",
            "pending": "#ffc89c",
            "processing": "#9cbeff",
            "no_status": "#ffffff",
        }
        TASK = (
            ARROW_TASK if dataspec.prototype() == sp.Dataset else SCALAR_TASK
        )
        stage = status.task(TASK) if status else None
        # Colors
        if stage is None:
            fillcolor = FILLCOLORS["no_status"]
            color = FILLCOLORS["error"]
        else:
            fillcolor = FILLCOLORS[stage.stage()]
            color = "black"

        # Labels
        if dataspec.prototype() == sp.Dataset:
            if dataspec.is_remote():
                label_type = "Source"
            elif dataspec.is_synthetic():
                label_type = "Synthetic data"
            else:
                label_type = "Transformed"
        else:
            label_type = "Scalar"
        label_type = label_type.replace('"', "'")

        symbol = symbols.get(dataspec.uuid())
        if symbol is None:
            symbol = "anonymous"

        if stage:
            msg = stage.properties().get("message", "").replace('"', "'")
        else:
            msg = "No status found."
        if msg:
            msg = "\n" + msg

        try:
            if dataspec.is_pep():
                label_type = f"{label_type} (PEP)"
        except NameError:
            # the transform is not included in the public SDS
            pass
        if self.dataspec_validator().is_dp(dataspec):
            label_type = f"{label_type} (DP)"

        label = f"{label_type}: {symbol}{msg}"

        return (
            f'"{dataspec.uuid()}"[label="{label}", '
            f'fillcolor="{fillcolor}", color="{color}", shape={shape}]'
        )

    async def async_schema_op(self, dataset: st.Dataset) -> st.Schema:
        # quickfix for select sql, to be removed when there is an endpoint
        # for schema
        if (
            dataset.is_transformed()
            and dataset.transform().spec() == 'select_sql'
        ):
            # push dataset
            computation_graph = self.computation_graph(dataset)
            referrables = (
                list(computation_graph["dataspecs"])
                + list(computation_graph["transforms"])
                + list(computation_graph["attributes"])
            )
            api.push_dataspec_graph(self._client, referrables)
            parent_schema = await self.async_schema(dataset.parents()[0][0])
            iterator = await self.async_to_arrow(dataset, batch_size=1000)
            table = pa.Table.from_batches([batch async for batch in iterator])
            fields = {
                col: type_from_arrow(
                    arrow_type=table.field(col).type,
                    nullable=table.field(col).nullable,
                )
                for col in table.schema.names
            }
            schema_type = sdt.Struct(fields=fields)
            return schema_builder(
                dataset,
                schema_type=schema_type,
                name=parent_schema.name(),
            )

        if dataset.is_transformed():
            return await TransformedDataset(dataset).schema()
        else:
            raise ValueError('Dataset should be transformed.')

    async def async_to_arrow_op(
        self, dataset: st.Dataset, batch_size: int
    ) -> t.AsyncIterator[pa.RecordBatch]:
        """Route a Dataset to its Op implementation.

        When the computation is not delegated the manager should also be
        able to compute the value.
        """
        if dataset.is_transformed():
            iterator = await TransformedDataset(dataset).to_arrow(
                batch_size=batch_size
            )
            return iterator

        else:
            raise ValueError('Dataset should be transformed.')

    async def async_value_op(self, scalar: st.Scalar) -> t.Any:
        """Route a Scalar to its Op implementation.

        This method is shared between API and Worker because when the data is
        not cached the API manager should also be able to compute the value.
        """
        if scalar.is_transformed():
            return await TransformedScalar(scalar).value()
        else:
            return await SourceScalar(scalar).value()

    def copy_status_from_server(
        self, dataspec: st.DataSpec, task_names: t.List[str]
    ) -> None:
        """This method is to be used only temporary to retrieve
        the schemas from the server when a dataset is created"""
        status = api.dataspec_status(
            self.client(), dataspec.uuid(), task_names=task_names
        )
        for task_name in task_names:
            if dataspec.status([task_name]) is None:
                stt.ready(
                    dataspec,
                    manager=self,
                    task=task_name,
                    properties=status.task_stages[task_name].properties,
                )

    def dataspec_computation(
        self,
        dataspec: st.DataSpec,
    ) -> BaseComputation:
        """Return the computation for a DataSpec."""
        proto = dataspec.prototype()
        if proto == sp.Dataset:
            return self.to_arrow_computation
        return self.value_computation

    def computation_timeout(self, dataspec: st.DataSpec) -> int:
        return 600

    def computation_max_delay(self, dataspec: st.DataSpec) -> int:
        return 10


def manager(
    storage: storage_typing.Storage, client, **kwargs: t.Any
) -> SDKManager:
    """Create the SDK manager."""
    properties = {"type": "sdk_manager"}
    properties.update(kwargs)
    return SDKManager(
        storage=storage,
        protobuf=sp.Manager(properties=properties),
        client=client,
    )
