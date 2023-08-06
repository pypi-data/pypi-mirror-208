from typing import List, Optional
import logging

from gql import gql

from navability.entities.client import Client
from navability.entities.navabilityclient import NavAbilityClient, QueryOptions
from navability.entities.user import User, UserSchema
from navability.services.loader import GQL_OPERATIONS

logger = logging.getLogger(__name__)


async def getUsers(navAbilityClient: NavAbilityClient):
    """Get all users that are accessible by this user.

    Args:
        navAbilityClient (NavAbilityClient): The NavAbility client.
    """
    users = await navAbilityClient.query(
        QueryOptions(GQL_OPERATIONS["QUERY_GET_USERS"].data)
    )
    schema = UserSchema(many=True)
    return schema.load(users["users"])


async def getUser(navAbilityClient: NavAbilityClient, userLabel: str) -> Optional[User] :
    """Get a user.

    Args:
        navAbilityClient (NavAbilityClient): The NavAbility client.
        userLabel (str): The email address of the user.
    """
    resp = await navAbilityClient.query(
        QueryOptions(GQL_OPERATIONS["QUERY_GET_USER"].data, {"userLabel": userLabel})
    )
    schema = UserSchema()
    if len(resp["users"]) != 1:
        logger.warn(f"No users returned for username ${userLabel}")
        return None
    return schema.load(resp["users"][0])
