import io
import json
import logging
import pickle as pkl
import time
import typing as t
from http import HTTPStatus

import pyarrow as pa
import pyarrow.parquet as pq
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st
from requests import Response
from sarus_data_spec.constants import (
    BEST_ALTERNATIVE,
    CONSTRAINT_KIND,
    PRIVACY_LIMIT,
)
from sarus_data_spec.dataspec_validator.typing import DataspecPrivacyPolicy
from sarus_data_spec.manager.async_utils import async_iter
from sarus_data_spec.protobuf.utilities import dict_deserialize, dict_serialize

from sarus.typing import Client

logger = logging.getLogger(__name__)


def raise_response(resp: Response) -> None:
    """Raise exception with message encapsulated in the response JSON data."""
    if resp.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
        resp.raise_for_status()
    if resp.status_code >= HTTPStatus.BAD_REQUEST:
        try:
            message = resp.json().get("message")
        except json.JSONDecodeError as e:
            resp.raise_for_status()
        if message is not None:
            raise ValueError(f"Server - {message}")
    resp.raise_for_status()


def get_dataspec(
    client: Client, uuid: str
) -> t.Tuple[t.Optional[st.DataSpec], float]:
    """Fetch a single Dataspec from the server."""
    start = time.perf_counter()
    resp: Response = client.session().get(
        f"{client.url()}/dataspecs/{uuid}",
    )
    end = time.perf_counter()
    logger.debug(
        f"GET /dataspecs/{uuid} {resp.status_code} ({end-start:.2f}s)"
    )
    if resp.status_code == HTTPStatus.NOT_FOUND:
        return None, 0.0

    raise_response(resp)

    proto = dict_deserialize(resp.json()["dataspec"])
    epsilon = resp.json()["epsilon"]
    return client.context().factory().create(proto), epsilon


def pull_dataspec_graph(client: Client, uuid: str) -> None:
    """Fetch a dataspec's computation graph and store it."""
    start = time.perf_counter()
    resp: Response = client.session().get(
        f"{client.url()}/dataspecs/{uuid}/graph",
    )
    end = time.perf_counter()
    logger.debug(
        f"GET /dataspecs/{uuid}/graph {resp.status_code} ({end-start:.2f}s)"
    )
    raise_response(resp)

    protos = [dict_deserialize(msg) for msg in resp.json()]
    referrables = [
        client.context().factory().create(proto, store=False)
        for proto in protos
    ]
    client.context().storage().batch_store(referrables)


def push_dataspec_graph(client: Client, graph: t.List[st.Referrable]) -> None:
    """Push a list of referrables to the server."""
    start = time.perf_counter()
    resp: Response = client.session().post(
        f"{client.url()}/dataspecs/graph",
        json=[dict_serialize(ref.protobuf()) for ref in graph],
    )
    end = time.perf_counter()
    logger.debug(
        f"POST /dataspecs/graph {resp.status_code} ({end-start:.2f}s)"
    )
    raise_response(resp)


def compile_dataspec(
    client: Client,
    uuid: str,
    constraint_kind: t.Optional[st.ConstraintKind] = None,
    privacy_limit: t.Optional[st.PrivacyLimit] = None,
) -> t.Tuple[str, t.Optional[DataspecPrivacyPolicy]]:
    """Compile the dataspec to abide privacy constraints.

    Return the compiled dataspec's UUID and the optional privacy policy name.
    """
    kind_name = constraint_kind.name if constraint_kind else BEST_ALTERNATIVE
    payload = {CONSTRAINT_KIND: kind_name}
    if privacy_limit is not None:
        payload[PRIVACY_LIMIT] = privacy_limit.delta_epsilon_dict()

    start = time.perf_counter()
    resp: Response = client.session().post(
        f"{client.url()}/dataspecs/{uuid}/compile",
        json=payload,
    )
    end = time.perf_counter()
    logger.debug(
        f"POST /dataspecs/{uuid}/compile {resp.status_code} ({end-start:.2f}s)"
    )
    raise_response(resp)

    pp_value = resp.json()["privacy_policy"]
    privacy_policy = DataspecPrivacyPolicy(pp_value) if pp_value else None

    return resp.json()["uuid"], privacy_policy


def launch_dataspec(client: Client, uuid: str) -> None:
    """Launch a Dataspec's computation on the server."""
    start = time.perf_counter()
    resp: Response = client.session().post(
        f"{client.url()}/dataspecs/{uuid}/launch",
    )
    end = time.perf_counter()
    logger.debug(
        f"POST /dataspecs/{uuid}/launch {resp.status_code} ({end-start:.2f}s)"
    )
    raise_response(resp)


def dataspec_status(
    client: Client, uuid: str, task_names: t.List[str]
) -> t.Optional[sp.Status]:
    """Get the dataspec's status on the server."""
    if type(task_names) not in [set, list, tuple]:
        raise TypeError("task_names should be a list of strings.")

    start = time.perf_counter()
    resp: Response = client.session().get(
        f"{client.url()}/dataspecs/{uuid}/status",
        params={"task_names": list(task_names)},
    )
    end = time.perf_counter()
    logger.debug(
        f"GET /dataspecs/{uuid}/status {resp.status_code} ({end-start:.2f}s)"
    )
    raise_response(resp)

    status_proto = resp.json().get("status")
    if status_proto is None:
        return None
    else:
        return dict_deserialize(status_proto)


def pull_dataspec_status_graph(
    client: Client, uuid: str, task_names: t.List[str]
) -> t.List[sp.Status]:
    """Fetch the server statuses of the computation graph's dataspecs."""
    if not type(task_names) in [list, set, tuple]:
        raise TypeError("task_names should be a list of strings.")

    start = time.perf_counter()
    resp: Response = client.session().get(
        f"{client.url()}/dataspecs/{uuid}/graph/statuses",
        params={"task_names": list(task_names)},
    )
    end = time.perf_counter()
    logger.debug(
        f"GET /dataspecs/{uuid}/graph/statuses {resp.status_code} ({end-start:.2f}s)"
    )
    raise_response(resp)

    return [dict_deserialize(msg) for msg in resp.json()]


def dataspec_result_response(
    client: Client, uuid: str, batch_size: t.Optional[int] = None
) -> Response:
    """Return the response result from the server.

    The response holds the dataspec's value and is read in the computation.
    """
    start = time.perf_counter()
    resp: Response = client.session().get(
        f"{client.url()}/dataspecs/{uuid}/result",
        params={"batch_size": batch_size},
        stream=True,
    )
    end = time.perf_counter()
    logger.debug(
        f"GET /dataspecs/{uuid}/result {resp.status_code} {resp.headers.get('Content-Type')} ({end-start:.2f}s)"
    )
    raise_response(resp)
    return resp


def dataset_result(
    client: Client, uuid: str, batch_size: int
) -> t.AsyncIterator[pa.RecordBatch]:
    """Return the dataset's value as a RecordBatch async iterator."""
    resp = dataspec_result_response(client, uuid, batch_size)
    if resp.headers.get("Content-Type") == "application/parquet":
        # Recieving Parquet file
        buffer = io.BytesIO()
        for data in resp.iter_content():
            buffer.write(data)
        buffer.seek(0)
        return async_iter(
            pq.read_table(buffer).to_batches(max_chunksize=batch_size)
        )
    else:
        # Recieving serialized streamed record batches
        async def arrow_iterator_from_response():
            with pa.ipc.open_stream(resp.raw) as reader:
                for batch in reader:
                    yield batch

        return arrow_iterator_from_response()


def scalar_result(client: Client, uuid: str) -> t.Any:
    """Return the scalar's value."""
    resp = dataspec_result_response(client, uuid)
    return pkl.loads(resp.content)
