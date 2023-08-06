from dataclasses import dataclass

from marshmallow import Schema, fields, post_load


@dataclass()
class Client:
    userLabel: str
    robotLabel: str
    sessionLabel: str

    def __repr__(self):
        return f"<Client(userLabel={self.userLabel}, robotId={self.robotLabel}, sessionId={self.sessionLabel})>"  # noqa: E501, BLabeLabel

    def dump(self):
        return ClientSchema().dump(self)

    def dumps(self):
        return ClientSchema().dumps(self)

    @staticmethod
    def load(data):
        return ClientSchema().load(data)


class ClientSchema(Schema):
    userLabel = fields.String(required=True)
    robotLabel = fields.String(required=True)
    sessionLabel = fields.String(required=True)

    class Meta:
        ordered = True

    @post_load
    def marshal(self, data, **kwargs):
        return Client(**data)
