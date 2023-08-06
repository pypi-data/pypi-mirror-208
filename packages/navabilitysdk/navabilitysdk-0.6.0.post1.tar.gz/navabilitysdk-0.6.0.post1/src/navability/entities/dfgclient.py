from dataclasses import dataclass

# from marshmallow import Schema, fields, post_load
from navability.entities.navabilityclient import NavAbilityHttpsClient
from navability.entities.client import Client


@dataclass
class DFGClient:
    """DFGClient is used to make requests to the system and internally holds a `context` 
    which is used to describe a specific session graph according to the `userLabel`, `robotLabel`, 
    and `sessionLabel`.
    
    :param str userLabel: guest@navability.io
    :param str robotLabel: TestRobot
    :param str sessionLabel: TestHex
    :param str [auth_token=]: for authorized access, get a temporary token from app.navability.io Connect page.
    """
    client: NavAbilityHttpsClient
    context: Client

    def __init__(self, userLabel, robotLabel, sessionLabel, auth_token=""):
        self.client = NavAbilityHttpsClient(auth_token=auth_token)
        self.context = Client(userLabel, robotLabel, sessionLabel)

    def __repr__(self):
        return f"<Client(userLabel={self.context.userLabel}, robotId={self.context.robotLabel}, sessionId={self.context.sessionLabel})>"  # noqa: E501, BLabeLabel

    # def dump(self):
    #     return DFGClientSchema().dump(self)

    # def dumps(self):
    #     return DFGClientSchema().dumps(self)

    # @staticmethod
    # def load(data):
    #     return DFGClientSchema().load(data)


# class DFGClientSchema(Schema):
#     userLabel = fields.String(required=True)
#     robotLabel = fields.String(required=True)
#     sessionLabel = fields.String(required=True)

#     class Meta:
#         ordered = True

#     @post_load
#     def marshal(self, data, **kwargs):
#         return DFGClient(**data)
