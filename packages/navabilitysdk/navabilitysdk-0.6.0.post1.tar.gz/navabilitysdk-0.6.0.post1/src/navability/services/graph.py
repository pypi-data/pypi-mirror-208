
import logging
from typing import List

import asyncio

from navability.entities.dfgclient import DFGClient
from navability.entities.navabilityclient import (
    QueryOptions,
    # MutationOptions,
    # NavAbilityClient,
)

from navability.services.loader import GQL_OPERATIONS

import nest_asyncio
nest_asyncio.apply()

logger = logging.getLogger(__name__)


async def listNeighborsAsync(fgclient: DFGClient, nodeLabel: str) -> List[str]:
    """Async vertion of listNeighbors
    """
    client = fgclient.client
    context = fgclient.context

    params = {
        "userLabel": context.userLabel,
        "robotLabel": context.robotLabel,
        "sessionLabel": context.sessionLabel,
        "nodeLabel": nodeLabel
    }

    logger.debug(f"Query params: {params}")
    res = await client.query(
        QueryOptions(GQL_OPERATIONS["QUERY_LIST_NEIGHBORS"].data, params)
    )

    logger.debug(f"Query result: {res}")
    # TODO: Check for errors
    # Using the hierarchy approach, we need to check that we
    # have exactly one user/robot/session in it, otherwise error.
    if (
        "variables" not in res
        or "factors" not in res
    ):
        raise Exception(
            "Received an empty data structure, set logger to debug for the payload"
        )

    flbls = [r for r in res["variables"][0]["factors"]] if (len(res["variables"]) > 0) else []

    vlbls = [r for r in res["factors"][0]["variables"]] if (len(res["factors"]) > 0) else []

    neigh_list = []
    _lb = lambda s: s['label']
    [neigh_list.append(_lb(f)) for f in flbls]
    [neigh_list.append(_lb(f)) for f in vlbls]

    return neigh_list


def listNeighbors(fgclient: DFGClient, nodeLabel: str) -> List[str]:
    """Returns a string list of neighbours to either a variable or a factor.

    Args:
        fgclient (DFGClient): client connection to API server with unique (user, robot, session) context.
        nodeLabel: List the neighbours of this variable or factor label.
    """
    tsk = listNeighborsAsync(fgclient, nodeLabel)
    return asyncio.run(tsk)
