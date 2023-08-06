import logging
from typing import List

import asyncio

from navability.services.loader import GQL_OPERATIONS
from navability.entities.dfgclient import DFGClient
from navability.entities.client import Client
from navability.entities.navabilityclient import (
    MutationOptions,
    NavAbilityClient,
    QueryOptions,
)
from navability.entities.querydetail import QueryDetail
from navability.entities.variable.variable import (
    Variable,
    VariableSchema,
    VariableSkeleton,
    VariableSkeletonSchema,
    VariableSummary,
    VariableSummarySchema,
    VariableType,
)

from navability.entities.variable.ppe import Ppe, PpeSchema

import nest_asyncio
nest_asyncio.apply()

DETAIL_SCHEMA = {
    QueryDetail.LABEL: None,
    QueryDetail.SKELETON: VariableSkeletonSchema(),
    QueryDetail.SUMMARY: VariableSummarySchema(),
    QueryDetail.FULL: VariableSchema(),
}

logger = logging.getLogger(__name__)


async def _addVariableAsync(
    navAbilityClient: NavAbilityClient,
    client: Client,
    v: Variable
):
    # {"variable": {"client": client.dump(), "packedData": v.dumpsPacked()}}
    sessionconnect = {
        "connect": {
            "where": {
                "node": {
                    "label": client.sessionLabel
                }
            }
        }
    }

    variableCreateInput = {
        'label': v.label,
        'nstime': v.nstime,
        'variableType': v.variableType,
        'solvable': v.solvable,
        'tags': v.tags,
        '_version': v._version,
        'timestamp': VariableSchema().get_timestamp(v),
        'userLabel': client.userLabel,
        'robotLabel': client.robotLabel,
        'sessionLabel': client.sessionLabel,
        'session': sessionconnect,
        'metadata': "e30=", #FIXME
        # 'ppes': Optional['VariablePpesFieldInput'],
        # 'blobEntries': Optional['VariableBlobEntriesFieldInput'],
        # 'solverData': Optional['VariableSolverDataFieldInput'],
        # 'factors': Optional['VariableFactorsFieldInput'],
    }

    params = {"variablesToCreate": [variableCreateInput]}

    result = await navAbilityClient.mutate(
        MutationOptions(
            GQL_OPERATIONS["MUTATION_ADD_VARIABLES"].data,
            params,
        )
    )
    return VariableSchema().load(result["addVariables"]["variables"][0])


def _addVariable(navAbilityClient: NavAbilityClient, client: Client, v: Variable):
    tsk = _addVariableAsync(navAbilityClient, client, v)
    return asyncio.run(tsk)


def addVariable(
    fgclient: DFGClient,
    variable_or_label,
    varType=None
):
    """ Add a variable to the graph.

    Args:
        client (NavAbilityClient): client connection to API server
        context (Client): Unique context with (user, robot, session)
        variable_or_label (Variable or string): The variable to add.
        varType (VariableType, optional): Pose2, Pose3, etc. Defaults to None.

    Raises:
        NotImplementedError: _description_

    Returns:
        _type_: _description_
    """
    client = fgclient.client
    context = fgclient.context

    if isinstance(variable_or_label, Variable):
        return _addVariable(client, context, variable_or_label)
    # TODO standardise varType to string or VariableType after design discussion
    if isinstance(varType, str):
        v = Variable(variable_or_label, varType)
        return _addVariable(client, context, v)
    elif isinstance(varType, VariableType):
        v = Variable(variable_or_label, varType.value)
        return _addVariable(client, context, v)
    raise NotImplementedError()


async def listVariablesAsync(
    fgclient: DFGClient,
    regexFilter: str = ".*",
    tags: List[str] = None,
    solvable: int = 0,
) -> List[str]:
    """Asynchronous version of listVariables.  Async task returning a string list of Variable labels.

    Args:
        fgclient (DFGClient): client connection to API server with unique (user, robot, session) context.
        regexFilter (str, optional): Filter on variable label. Defaults to ".*".
        tags (List[str], optional): Variables can have string tags. Defaults to None.
        solvable (int, optional): Whether this variable can be used in solving yet. Defaults to 0.
    """

    client = fgclient.client
    context = fgclient.context
    
    params = {
        "userLabel": context.userLabel,
        "robotLabel": context.robotLabel,
        "sessionLabel": context.sessionLabel,
    }
    logger.debug(f"Query params: {params}")
    res = await client.query(
        QueryOptions(GQL_OPERATIONS["QUERY_LIST_VARIABLES"].data, params)
    )
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
    vl = []
    _lb = lambda s: s['label']
    resvar = res['users'][0]['robots'][0]['sessions'][0]['variables']
    [vl.append(_lb(v)) for v in resvar]
    return vl


def listVariables(
    fgclient: DFGClient,
    regexFilter: str = ".*",
    tags: List[str] = None,
    solvable: int = 0,
) -> List[str]:
    """Returns a string list of Variable labels.

    Args:
        fgclient (DFGClient): client connection to API server with unique (user, robot, session) context.
        regexFilter (str, optional): Filter on variable label. Defaults to ".*".
        tags (List[str], optional): Variables can have string tags. Defaults to None.
        solvable (int, optional): Whether this variable can be used in solving yet. Defaults to 0.
    """
    tsk = listVariablesAsync(fgclient, regexFilter, tags, solvable)
    return asyncio.run(tsk)





# Alias
ls = listVariables


async def getVariablesAsync(
    fgclient: DFGClient,
    detail: QueryDetail = QueryDetail.FULL,
    regexFilter: str = ".*",
    tags: List[str] = None,
    solvable: int = 0,
) -> List[VariableSkeleton]:
    """Get a list of Variable from a graph using various filters.

    Args:
        client (NavAbilityClient): client connection to API server
        context (Client): Unique context with (user, robot, session)
        detail (QueryDetail, optional): Defaults to QueryDetail.SKELETON.
        regexFilter (str, optional): Filter on variable label. Defaults to ".*".
        tags (List[str], optional): Variables can have string tags. Defaults to None.
        solvable (int, optional): Whether this variable can be used in solving yet.
        Defaults to 0.

    Returns:
        List[VariableSkeleton]: Async task returning a list of VariableSkeleton
    """

    client = fgclient.client
    context = fgclient.context

    params = {
        "userLabel": context.userLabel,
        "robotLabel": context.robotLabel,
        "sessionLabel": context.sessionLabel,
        "variable_label_regexp": regexFilter,
        "variable_tags": tags if tags is not None else ["VARIABLE"],
        "solvable": solvable,
        "fields_summary": detail in [QueryDetail.SUMMARY, QueryDetail.FULL],
        "fields_full": detail == QueryDetail.FULL,
    }
    logger.debug(f"Query params: {params}")
    res = await client.query(
        QueryOptions(GQL_OPERATIONS["QUERY_GET_VARIABLES"].data, params))
    logger.debug(f"Query result: {res}")
    # TODO: Check for errors
    schema = DETAIL_SCHEMA[detail]
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
    if schema is None:
        return res["users"][0]["robots"][0]["sessions"][0]["variables"]
    return [
        schema.load(l) for l in res["users"][0]["robots"][0]["sessions"][0]["variables"]
    ]


def getVariables(
    fgclient: DFGClient,
    detail: QueryDetail = QueryDetail.FULL,
    regexFilter: str = ".*",
    tags: List[str] = None,
    solvable: int = 0,
) -> List[VariableSkeleton]:

    tsk = getVariablesAsync(fgclient, detail, regexFilter, tags, solvable)
    return asyncio.run(tsk)


def getVariablesSummary(
    fgclient: DFGClient,
    regexFilter: str = ".*",
    tags: List[str] = None,
    solvable: int = 0,
) -> List[VariableSkeleton]:
    tsk = getVariablesAsync(fgclient, QueryDetail.SUMMARY, regexFilter, tags, solvable)
    return asyncio.run(tsk)


def getVariablesSkeleton(
    fgclient: DFGClient,
    regexFilter: str = ".*",
    tags: List[str] = None,
    solvable: int = 0,
) -> List[VariableSkeleton]:
    tsk = getVariablesAsync(fgclient, QueryDetail.SKELETON, regexFilter, tags, solvable)
    return asyncio.run(tsk)


async def getVariableAsync(
    fgclient: DFGClient,
    label: str
):
    """Get a Variable object from the server as connect to via fgclient.
    
    :param DFGClient fgclient: connection to servers, containing (user, robot, session) context.
    :param str label: Variable label to retrieve.

    Returns:
        Variable: Multilanguage standardized Variable format.
    """
    client = fgclient.client
    context = fgclient.context

    params = context.dump()
    params["variableLabel"] = label
    logger.debug(f"Query params: {params}")
    res = await client.query(
        QueryOptions(GQL_OPERATIONS["QUERY_GET_VARIABLE"].data, params))
    logger.debug(f"Query result: {res}")
    # TODO: Check for errors
    # Using the hierarchy approach, we need to check that we have
    # exactly one user/robot/session in it, otherwise error.
    if (
        "users" not in res
        or len(res["users"][0]["robots"]) != 1
        or len(res["users"][0]["robots"][0]["sessions"]) != 1
        or "variables" not in res["users"][0]["robots"][0]["sessions"][0]
    ):
        raise Exception(
            "Received an empty data structure, set logger to debug for the payload"
        )
    vs = res["users"][0]["robots"][0]["sessions"][0]["variables"]
    # TODO: Check for errors
    if len(vs) == 0:
        return None
    if len(vs) > 1:
        raise Exception(f"More than one variable named {label} returned")
    return Variable.load(vs[0])


def getVariable(
    fgclient: DFGClient,
    label: str
):
    tsk = getVariableAsync(fgclient, label)
    return asyncio.run(tsk)


# TODO maybe move to seperate ppe.py file

def getPPE(
    fgclient: DFGClient, 
    variableLabel: str, 
    solveKey: str = 'default'
):
    client = fgclient.client
    context = fgclient.context

    params = {
        "userLabel": context.userLabel,
        "robotLabel": context.robotLabel,
        "sessionLabel": context.sessionLabel,
        "variableLabel": variableLabel,
        "solveKey": solveKey,
    }
    logger.debug(f"Query params: {params}")
    tsk = client.query(QueryOptions(GQL_OPERATIONS["QUERY_GET_PPE"].data, params))
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

    ppes = res["users"][0]["robots"][0]["sessions"][0]["variables"][0]["ppes"]

    if len(ppes) == 0:
        return None
    if len(ppes) > 1:
        raise Exception(f"More than one variable named {solveKey} returned")

    return Ppe.load(ppes[0])

