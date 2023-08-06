from dataclasses import dataclass

from marshmallow import Schema, fields, post_load


@dataclass()
class SolveOptions:
    key: str
    useParametric: bool

    def __repr__(self):
        return f"<SolveOptions(key={self.key}, useParametric={self.useParametric})>"  # noqa: E501, B950

    def dump(self):
        return SolveOptionsSchema().dump(self)

    def dumps(self):
        return SolveOptionsSchema().dumps(self)

    @staticmethod
    def load(data):
        return SolveOptionsSchema().load(data)


class SolveOptionsSchema(Schema):
    key = fields.String(required=True)
    useParametric = fields.Bool(required=True)

    class Meta:
        ordered = True

    @post_load
    def marshal(self, data, **kwargs):
        return SolveOptions(**data)
