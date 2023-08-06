import logging
from typing import List
from uuid import uuid4

from gql import gql

import asyncio

from navability.entities.dfgclient import DFGClient

from navability.entities.client import Client

from navability.services.loader import GQL_OPERATIONS
from navability.entities.factor.factor import (
    Factor,
    FactorData,
    FactorSchema,
    FactorSkeleton,
    FactorSkeletonSchema,
    FactorSummarySchema,
)
from navability.entities.factor.inferencetypes import InferenceType
from navability.entities.navabilityclient import (
    MutationOptions,
    NavAbilityClient,
    QueryOptions,
)
from navability.entities.querydetail import QueryDetail

import nest_asyncio
nest_asyncio.apply()

DETAIL_SCHEMA = {
    QueryDetail.LABEL: None,
    QueryDetail.SKELETON: FactorSkeletonSchema(),
    QueryDetail.SUMMARY: FactorSummarySchema(),
    QueryDetail.FULL: FactorSchema(),
}

logger = logging.getLogger(__name__)


async def getFactorAsync(fgclient: DFGClient, label: str, debug=False):

    client = fgclient.client
    context = fgclient.context

    params = {
        "userLabel": context.userLabel,
        "robotLabel": context.robotLabel,
        "sessionLabel": context.sessionLabel,
        "label": label,
        # "fields_summary": detail in [QueryDetail.SUMMARY, QueryDetail.FULL],
        # "fields_full": detail == QueryDetail.FULL,
    }

    logger.debug(f"Query params: {params}")
    res = await client.query(
        QueryOptions(GQL_OPERATIONS["QUERY_GET_FACTOR"].data, params)
    )

    logger.debug(f"Query result: {res}")
    # TODO: Check for errors
    # Using the hierarchy approach, we need to check that we
    # have exactly one user/robot/session in it, otherwise error.
    if (
        "users" not in res
        or len(res["users"][0]["robots"]) != 1
        or len(res["users"][0]["robots"][0]["sessions"]) != 1
        or "factors" not in res["users"][0]["robots"][0]["sessions"][0]
    ):
        raise Exception(
            "Received an empty data structure, set logger to debug for the payload"
        )
    fs = res["users"][0]["robots"][0]["sessions"][0]["factors"]
    # TODO: Check for errors
    if len(fs) == 0:
        return None
    if len(fs) > 1:
        raise Exception(f"More than one factor named {label} returned")
    if debug:
        return fs[0]
    return Factor.load(fs[0])


def getFactor(fgclient: DFGClient, label: str, debug=False):
    tsk = getFactorAsync(fgclient, label, debug=debug)
    return asyncio.run(tsk)


async def listFactorsAsync(fgclient: DFGClient) -> List[str]:

    client = fgclient.client
    context = fgclient.context

    params = {
        "userLabel": context.userLabel,
        "robotLabel": context.robotLabel,
        "sessionLabel": context.sessionLabel,
    }

    logger.debug(f"Query params: {params}")
    res = await client.query(
        QueryOptions(GQL_OPERATIONS["QUERY_LISTFACTORS"].data, params)
    )

    logger.debug(f"Query result: {res}")
    # TODO: Check for errors
    # Using the hierarchy approach, we need to check that we
    # have exactly one user/robot/session in it, otherwise error.
    if (
        "users" not in res
        or len(res["users"][0]["robots"]) != 1
        or len(res["users"][0]["robots"][0]["sessions"]) != 1
        or "factors" not in res["users"][0]["robots"][0]["sessions"][0]
    ):
        raise Exception(
            "Received an empty data structure, set logger to debug for the payload"
        )
    fs = res["users"][0]["robots"][0]["sessions"][0]["factors"]

    fl = []
    _lb = lambda s: s['label']
    [fl.append(_lb(f)) for f in fs]
    return fl


def listFactors(fgclient: DFGClient):
    tsk = listFactorsAsync(fgclient)
    return asyncio.run(tsk)


# Alias
lsf = listFactors


def assembleFactorName(xisyms: List[str]):
    s = "".join(xisyms) + "f_" + str(uuid4())[0:4]
    return s


def getFncTypeName(fnc: InferenceType):
    return type(fnc).__name__


async def _addFactorAsync(
    client: NavAbilityClient,
    context: Client,
    f: Factor,
):
    sessionconnect = {
        "connect": {
            "where": {
                "node": {
                    "label": context.sessionLabel
                }
            }
        }
    }

    variables = {
        "connect": [
            {
                "where": {
                    "node": {
                        "sessionConnection": {"node": {"label": context.sessionLabel}},
                        "label": vlink
                    }
                }
            }
            for vlink in f._variableOrderSymbols
        ]
    }

    factorCreateInput = {
        'label': f.label,
        'nstime': f.nstime,
        'fnctype': f.fnctype,
        'tags': f.tags,
        'solvable': f.solvable,
        'data': FactorSchema().get_data(f),
        '_variableOrderSymbols': f._variableOrderSymbols,
        'timestamp': FactorSchema().get_timestamp(f),
        '_type': f.fnctype,
        '_version': f._version,
        'userLabel': context.userLabel,
        'robotLabel': context.robotLabel,
        'sessionLabel': context.sessionLabel,
        'variables': variables,
        'session': sessionconnect,
        'metadata': "e30=", #FIXME
        # 'blobEntries': Optional['FactorBlobEntriesFieldInput'],
    }

    params = {"factorsToCreate": [factorCreateInput]}

    result = await client.mutate(
        MutationOptions(
            GQL_OPERATIONS["MUTATION_ADD_FACTORS"].data,
            params,
        )
    )
    #FIXME
    # return FactorSchema().load(result["addFactors"]["factors"][0])
    return result["addFactors"]["factors"][0]


def addFactorAsync(
    fgclient: DFGClient,
    factor_or_labels,
    fnc=None,
    multihypo=None,
    nullhypo=0.0,
):
    client = fgclient.client
    context = fgclient.context

    if isinstance(factor_or_labels, Factor):
        return _addFactorAsync(client, context, factor_or_labels)
    elif fnc is not None:
        fac = Factor(
            assembleFactorName(factor_or_labels),
            getFncTypeName(fnc),
            factor_or_labels,
            FactorData(
                fnc=fnc.dump(),
                multihypo=([] if multihypo is None else multihypo),
                nullhypo=nullhypo,
            ),
        )
        return _addFactorAsync(client, context, fac)
    else:
        raise NotImplementedError()


def addFactor(
    fgclient: DFGClient,
    factor_or_labels,
    fnc=None,
    multihypo=None,
    nullhypo=0.0,
):
    tsk = addFactorAsync(fgclient, factor_or_labels, fnc, multihypo, nullhypo)
    return asyncio.run(tsk)


async def getFactorsAsync(
    fgclient: DFGClient,
    # regexFilter: str = ".*",
    # tags: List[str] = None,
    # solvable: int = 0,
):
    client = fgclient.client
    context = fgclient.context

    params = {
        "userLabel": context.userLabel,
        "robotLabel": context.robotLabel,
        "sessionLabel": context.sessionLabel,
        # "factor_label_regexp": regexFilter,
        # "factor_tags": tags if tags is not None else ["FACTOR"],
        # "solvable": solvable,
        # "fields_summary": detail in [QueryDetail.SUMMARY, QueryDetail.FULL],
        # "fields_full": detail == QueryDetail.FULL,
    }

    logger.debug(f"Query params: {params}")
    res = await client.query(
        QueryOptions(GQL_OPERATIONS["QUERY_GET_FACTORS"].data, params)
    )
    logger.debug(f"Query result: {res}")

    # Using the hierarchy approach, we need to check that
    # we have exactly one user/robot/session in it, otherwise error.
    if (
        "users" not in res
        or len(res["users"]) != 1
        or len(res["users"][0]["robots"]) != 1
        or len(res["users"][0]["robots"][0]["sessions"]) != 1
        or "factors" not in res["users"][0]["robots"][0]["sessions"][0]
    ):
        # Debugging information
        if len(res["users"]) != 1:
            logger.warn("User not found in result, returning empty list")
        if len(res["users"][0]["robots"]) != 1:
            logger.warn("Robot not found in result, returning empty list")
        if len(res["users"][0]["robots"][0]["sessions"]) != 1:
            logger.warn("Robot not found in result, returning empty list")
        return []

    return [Factor.load(fac) for fac in res["users"][0]["robots"][0]["sessions"][0]["factors"]]


def getFactors(fgclient: DFGClient):
    tsk = getFactorsAsync(fgclient)
    return asyncio.run(tsk)
