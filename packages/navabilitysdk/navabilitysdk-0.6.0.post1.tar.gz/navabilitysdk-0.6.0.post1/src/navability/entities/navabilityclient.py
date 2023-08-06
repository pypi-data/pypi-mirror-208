import logging
from dataclasses import dataclass

from gql import Client as GQLCLient
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.websockets import WebsocketsTransport

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class QueryOptions:
    query: str
    variables: any = None
    fetchPolicy: any = None


@dataclass(frozen=True)
class MutationOptions:
    mutation: str
    variables: any = None
    fetchPolicy: any = None


class NavAbilityClient:
    def query(self, options: QueryOptions):
        pass

    def mutate(self, options: MutationOptions):
        pass


class NavAbilityWebsocketClient(NavAbilityClient):
    def __init__(self, url: str = "wss://api.navability.io/graphql") -> None:
        super().__init__()
        self.transport = WebsocketsTransport(url=url)

    async def query(self, options: QueryOptions):
        async with GQLCLient(
            transport=self.transport, fetch_schema_from_transport=False
        ) as client:
            logger.debug(
                f"Calling query {options.query} with args: {options.variables}"
            )
            result = await client.execute(options.query, options.variables)
            return result

    async def mutate(self, options: MutationOptions):
        async with GQLCLient(
            transport=self.transport, fetch_schema_from_transport=False
        ) as client:
            logger.debug(
                f"Calling mutation {options.mutation} with args: {options.variables}"
            )
            result = await client.execute(options.mutation, options.variables)
            return result


class NavAbilityHttpsClient(NavAbilityClient):
    """Connection object for queries and mutations to API server.  Note, this is used but higher level objects such as DFGClient.

    Args:
        NavAbilityClient: the connection object to a server (cloud our deployed).
        url: Network path to the API (cloud or deployed).
        auth_token: Token for auth, likely provided by NavAbility App Connect page.
    """
    def __init__(self, url: str = "https://api.navability.io", auth_token: str = "") -> None:
        super().__init__()
        if len(auth_token) == 0:
            self.transport = AIOHTTPTransport(
                url=url,
            )
        else:
            self.transport = AIOHTTPTransport(
                url=url,
                headers={'Authorization': 'Bearer '+auth_token}
            )

    async def query(self, options: QueryOptions):
        async with GQLCLient(
            transport=self.transport, fetch_schema_from_transport=True
        ) as client:
            result = await client.execute(options.query, options.variables)
            return result

    async def mutate(self, options: MutationOptions):
        async with GQLCLient(
            transport=self.transport, fetch_schema_from_transport=True
        ) as client:
            result = await client.execute(options.mutation, options.variables)
            return result
