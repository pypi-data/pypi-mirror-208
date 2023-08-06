from typing import List, Optional
import logging
from uuid import UUID

# from gql import gql

from navability.entities.navabilityclient import NavAbilityClient, QueryOptions
from navability.entities.map.map import Map, MapSchema
from navability.services.loader import GQL_OPERATIONS

logger = logging.getLogger(__name__)


async def getMaps(navAbilityClient: NavAbilityClient, userId: UUID) -> List[Map]:
    """Get all maps that are accessible by this user.

    Args:
        navAbilityClient (NavAbilityClient): The NavAbility client.
    """
    resp = await navAbilityClient.query(
        QueryOptions(GQL_OPERATIONS["QUERY_GET_MAPS"].data, {"userId": str(userId)})
    )

    schema = MapSchema(many=True)

    if (
        resp.get("users") is None
        or len(resp["users"]) != 1
        or resp["users"][0].get("maps") is None
    ):
        raise Exception("The query did not return a user or a list of maps")

    print(resp["users"][0]["maps"])

    return schema.load(resp["users"][0]["maps"])


async def getMap(
    navAbilityClient: NavAbilityClient, userId: UUID, mapId: UUID
) -> Optional[Map]:
    """Get a map.

    Args:
        navAbilityClient (NavAbilityClient): The NavAbility client.
        userId (UUID): The id of the user.
        mapId (UUID): The id of the map.
    """
    resp = await navAbilityClient.query(
        QueryOptions(
            GQL_OPERATIONS["QUERY_GET_MAP"].data,
            {"userId": str(userId), "mapId": str(mapId)},
        )
    )
    print("HERE!")
    print(resp)

    schema = MapSchema()

    if (
        resp.get("users") is None
        or len(resp["users"]) != 1
        or resp["users"][0].get("maps") is None
        or len(resp["users"][0]["maps"]) != 1
    ):
        logger.warn(f"No map with Id({mapId}) returned for user with Id(${userId})")
        raise Exception(f"No map with Id({mapId}) returned for user with Id(${userId})")
    map = resp["users"][0]["maps"][0]

    return schema.load(map)
