import asyncio
import logging

from navability.services.loader import GQL_OPERATIONS

from navability.entities.dfgclient import DFGClient

from navability.entities.blob.blobentry import BlobEntry
from navability.entities.navabilityclient import (
    MutationOptions,
    NavAbilityClient,
    QueryOptions,
)

from navability.entities.client import Client

import nest_asyncio
nest_asyncio.apply()

logger = logging.getLogger(__name__)


def getBlobEntry(
    fgclient: DFGClient,
    variableLabel: str,
    label: str,
):
    client = fgclient.client
    context = fgclient.context

    params = {
        "userLabel": context.userLabel,
        "robotLabel": context.robotLabel,
        "sessionLabel": context.sessionLabel,
        "variableLabel": variableLabel,
        "blobLabel": label,
    }
    logger.debug(f"Query params: {params}")
    tsk = client.query(QueryOptions(GQL_OPERATIONS["QUERY_GET_BLOBENTRY"].data, params))
    res = asyncio.run(tsk)
    logger.debug(f"Query result: {res}")
    # TODO: Check for errors
    # Using the hierarchy approach, we need to check that we have
    # exactly one user/robot/session in it, otherwise error.
    if (
        "users" not in res
        or len(res["users"]) != 1
        or len(res["users"][0]["robots"]) != 1
        or len(res["users"][0]["robots"][0]["sessions"]) != 1
        or "variables" not in res["users"][0]["robots"][0]["sessions"][0]
    ):
        # Debugging information
        if len(res["users"]) != 1:
            logger.warn("User not found in result, returning empty list")
        if len(res["users"][0]["robots"]) != 1:
            logger.warn("Robot not found in result, returning empty list")
        if len(res["users"][0]["robots"][0]["sessions"]) != 1:
            logger.warn("Robot not found in result, returning empty list")
        return []

    entries = res["users"][0]["robots"][0]["sessions"][0]["variables"][0]["blobEntries"]

    if len(entries) == 0:
        return None
    if len(entries) > 1:
        raise Exception(f"More than one variable named {label} returned")

    return BlobEntry.load(entries[0])


async def listBlobEntriesAsync(
    fgclient: DFGClient,
    variableLabel: str,
):
    """ Return a list of `BlobEntry` labels (asynchronous version).

    Args:
        fgclient (DFGClient): client connection to API server
            with unique context (user, robot, session)
        variableLabel (string): list data entries connected to which variable
    """
    client = fgclient.client
    context = fgclient.context

    params = {
        "userLabel": context.userLabel,
        "robotLabel": context.robotLabel,
        "sessionLabel": context.sessionLabel,
        "variableLabel": variableLabel,
    }
    logger.debug(f"Query params: {params}")

    res = await client.query(
        QueryOptions(GQL_OPERATIONS["QUERY_LIST_BLOBENTRIES"].data, params)
    )
    # res = # asyncio.run(tsk)
    # Using the hierarchy approach, we need to check that we have
    # exactly one user/robot/session in it, otherwise error.
    if (
        "users" not in res
        or len(res["users"]) != 1
        or len(res["users"][0]["robots"]) != 1
        or len(res["users"][0]["robots"][0]["sessions"]) != 1
        or "variables" not in res["users"][0]["robots"][0]["sessions"][0]
    ):
        # Debugging information
        if len(res["users"]) != 1:
            logger.warn("User not found in result, returning empty list")
        if len(res["users"][0]["robots"]) != 1:
            logger.warn("Robot not found in result, returning empty list")
        if len(res["users"][0]["robots"][0]["sessions"]) != 1:
            logger.warn("Robot not found in result, returning empty list")
        return []

    # extract result
    entries = res['users'][0]['robots'][0]['sessions'][0]['variables'][0]['blobEntries']

    return [
        entry['label'] for entry in entries
    ]

def listBlobEntries(
    fgclient: DFGClient,
    variableLabel: str,
):
    """ Return a list of `BlobEntry` labels (synchronous version).

    Args:
        fgclient (DFGClient): client connection to API server
            with unique context (user, robot, session)
        variableLabel (string): list data entries connected to which variable
    """
    tsk = listBlobEntriesAsync(fgclient, variableLabel)
    return asyncio.run(tsk)

# TODO 
# async def addBlobEntry(
#     client: NavAbilityClient,
#     context: Client,
#     variableLabel: str,
#     blobId: str,
#     blobLabel: str,
#     blobSize: int,
#     mimeType: str,
# ):
#     """ Add a BlobEntry to a specific variable node in the graph.

#     Args:
#         client (NavAbilityClient): client connection to API server
#         context (Client): Unique context with (user, robot, session)
#         variableLabel (string): list data entries connected to which variable.
#         blobId (String): The unique blob identifier of the data.
#         blobLabel (str): blob label.
#         blobSize (int): number of bytes.
#         mimeType (str): standard MIME definition of data.

#     Returns:
#         BlobEntry: coroutine 
#     """
#     params = {
#         "userId": context.userId,
#         "blobId": blobId,
#         "robotId": context.robotId,
#         "sessionId": context.sessionId,
#         "variableLabel": variableLabel,
#         "blobLabel": blobLabel,
#         "blobSize": blobSize,
#         "mimeType": mimeType,
#     }
#     logger.debug(f"Query params: {params}")
#     res = await client.mutate(
#         MutationOptions(
#             gql(GQL_ADDBLOBENTRY),
#             params,
#         )
#     )
#     # TODO error handling
#     # if 'errors' in res:
#     #     raise Exception('Unable to addBlobEntry: '+res['errors'])
#     print(res)

#     return res['addBlobEntry']['context']['eventId']

