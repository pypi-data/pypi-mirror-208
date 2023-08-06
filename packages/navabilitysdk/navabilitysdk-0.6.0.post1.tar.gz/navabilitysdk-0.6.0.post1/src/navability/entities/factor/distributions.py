from dataclasses import dataclass, field
from typing import List

import numpy
from marshmallow import Schema, fields, post_load


class Distribution:
    """
    Base type for all distribution classes.
    """

    def dumpsPacked(self):
        raise Exception(f"'dumpsPacked' has not been implemented in {str(type(self))}")


class NormalSchema(Schema):
    _type = fields.String(default="IncrementalInference.PackedNormal")
    mu = fields.Float()
    sigma = fields.Float()

    @post_load
    def marshal(self, data, **kwargs):
        return Normal(**data)

    class Meta:
        ordered = True


@dataclass
class Normal(Distribution):
    mu: float
    sigma: float
    _type: str = "IncrementalInference.PackedNormal"

    def dumps(self):
        return NormalSchema().dumps(self)

    def dump(self):
        return NormalSchema().dump(self)

    @staticmethod
    def load(data):
        return NormalSchema().load(data)


class RayleighSchema(Schema):
    _type = fields.String(default="IncrementalInference.PackedRayleigh")
    sigma = fields.Float()

    @post_load
    def marshal(self, data, **kwargs):
        return Normal(**data)

    class Meta:
        ordered = True


@dataclass
class Rayleigh(Distribution):
    sigma: float
    _type: str = "IncrementalInference.PackedRayleigh"

    def dumps(self):
        return RayleighSchema().dumps(self)

    def dump(self):
        return RayleighSchema().dump(self)

    @staticmethod
    def load(data):
        return RayleighSchema().load(data)


class FullNormalSchema(Schema):
    _type = fields.String(default="IncrementalInference.PackedFullNormal")
    mu = fields.List(fields.Float)
    cov = fields.Method("get_cov", "set_cov", required=True)

    def get_cov(self, obj):
        return obj.cov.flatten().tolist()

    def set_cov(self, obj):
        raise Exception("Deserialization not supported yet.")  # obj.cov.reshape(3,3)?

    class Meta:
        ordered = True

    @post_load
    def marshal(self, data, **kwargs):
        return FullNormal(**data)


@dataclass
class FullNormal(Distribution):
    # TODO: Remove the default initializers.
    mu: numpy.ndarray = field(default_factory=lambda: numpy.zeros(3))
    cov: numpy.ndarray = field(default_factory=lambda: numpy.diag([0.1, 0.1, 0.1]))
    _type: str = "IncrementalInference.PackedFullNormal"

    def dumps(self):
        return FullNormalSchema().dumps(self)

    def dump(self):
        return FullNormalSchema().dump(self)

    @staticmethod
    def load(data):
        return FullNormalSchema().load(data)


@dataclass
class Uniform(Distribution):
    a: float
    b: float

    def dumps(self):
        return UniformSchema().dumps(self)

    def dump(self):
        return UniformSchema().dump(self)

    @staticmethod
    def load(data):
        return UniformSchema().load(data)


class UniformSchema(Schema):
    _type = fields.String(default="IncrementalInference.PackedUniform")
    a = fields.Float()
    b = fields.Float()
    PackedSamplableTypeJSON = fields.String(
        default="IncrementalInference.PackedUniform"
    )

    class Meta:
        ordered = True


@dataclass
class Categorical(Distribution):
    p: List[float]

    def dumps(self):
        return CategoricalSchema().dumps(self)

    def dump(self):
        return CategoricalSchema().dump(self)

    @staticmethod
    def load(data):
        return CategoricalSchema().load(data)


class CategoricalSchema(Schema):
    _type = fields.String(default="IncrementalInference.PackedCategorical")
    p = fields.List(fields.Float)

    class Meta:
        ordered = True
