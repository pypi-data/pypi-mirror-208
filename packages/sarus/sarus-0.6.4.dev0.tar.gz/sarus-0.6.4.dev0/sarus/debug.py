import logging
import typing as t

import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st

from sarus.typing import Client

logger = logging.getLogger()


def dot(client: Client, uuid: str) -> t.Any:
    referrable = client.context().storage().referrable(uuid)
    if referrable is None:
        logger.error(f"{uuid} is not found in the Client storage.")

    if referrable.prototype() not in [sp.Dataset, sp.Scalar]:
        logger.error(f"{uuid} is not a Dataspec: {referrable.prototype()}")

    dataspec = t.cast(st.DataSpec, referrable)

    try:
        from graphviz import Source
    except:
        logger.warning("Graphviz not installed. Cannot plot dot graph.")
        return

    return Source(dataspec.dot())
