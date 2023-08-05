from typing import Any, Dict, List, Optional

from sarus_data_spec.dataspec_validator.signature import (
    SarusBoundSignature,
    SarusParameter,
    SarusParameterArray,
    SarusParameterMapping,
    SarusSignature,
)
from sarus_data_spec.dataspec_validator.typing import PEPKind

from .external_op import ExternalOpImplementation


class add(ExternalOpImplementation):
    _transform_id = "std.ADD"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return this + other

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class sub(ExternalOpImplementation):
    _transform_id = "std.SUB"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return this - other

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class rsub(ExternalOpImplementation):
    _transform_id = "std.RSUB"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return other - this

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class mul(ExternalOpImplementation):
    _transform_id = "std.MUL"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return this * other

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class div(ExternalOpImplementation):
    _transform_id = "std.DIV"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return this / other

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class rdiv(ExternalOpImplementation):
    _transform_id = "std.RDIV"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return other / this

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class invert(ExternalOpImplementation):
    _transform_id = "std.INVERT"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        (this,) = await signature.collect_args()
        return ~this

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class length(ExternalOpImplementation):
    _transform_id = "std.LEN"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        (this,) = await signature.collect_args()
        return len(this)


class getitem(ExternalOpImplementation):
    _transform_id = "std.GETITEM"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="key",
            annotation=Any,
        ),
        name=_transform_id,
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, key = await signature.collect_args()
        return this[key]


class setitem(ExternalOpImplementation):
    _transform_id = "std.SETITEM"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="key",
            annotation=Any,
        ),
        SarusParameter(
            name="value",
            annotation=Any,
        ),
        name=_transform_id,
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, key, value = await signature.collect_args()
        this[key] = value
        return this


class greater_than(ExternalOpImplementation):
    _transform_id = "std.GT"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return this > other

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class greater_equal(ExternalOpImplementation):
    _transform_id = "std.GE"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return this >= other

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class lower_than(ExternalOpImplementation):
    _transform_id = "std.LT"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return this < other

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class lower_equal(ExternalOpImplementation):
    _transform_id = "std.LE"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return this <= other

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class not_equal(ExternalOpImplementation):
    _transform_id = "std.NE"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return this != other

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class neg(ExternalOpImplementation):
    _transform_id = "std.NEG"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        (this,) = await signature.collect_args()
        return -this

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class pos(ExternalOpImplementation):
    _transform_id = "std.POS"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        (this,) = await signature.collect_args()
        return +this

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class _abs(ExternalOpImplementation):
    _transform_id = "std.ABS"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        (this,) = await signature.collect_args()
        return abs(this)

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class _round(ExternalOpImplementation):
    _transform_id = "std.ROUND"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        (this,) = await signature.collect_args()
        return round(this)

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class modulo(ExternalOpImplementation):
    _transform_id = "std.MOD"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return this % other

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class rmodulo(ExternalOpImplementation):
    _transform_id = "std.RMOD"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return other % this

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class _or(ExternalOpImplementation):
    _transform_id = "std.OR"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return this | other

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class ror(ExternalOpImplementation):
    _transform_id = "std.ROR"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return other | this

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class _and(ExternalOpImplementation):
    _transform_id = "std.AND"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return this & other

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class rand(ExternalOpImplementation):
    _transform_id = "std.RAND"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        this, other = await signature.collect_args()
        return other & this

    def pep_kind(self, bound_signature: SarusBoundSignature) -> PEPKind:
        return PEPKind.TOKEN_PRESERVING


class _int(ExternalOpImplementation):
    _transform_id = "std.INT"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        (this,) = await signature.collect_args()
        return int(this)


class _float(ExternalOpImplementation):
    _transform_id = "std.FLOAT"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        (this,) = await signature.collect_args()
        return float(this)


class _list(ExternalOpImplementation):
    _transform_id = "std.LIST"
    _signature = SarusSignature(
        SarusParameterArray(
            name="elem",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        elems = await signature.collect_args()
        return list(elems)


class _dict(ExternalOpImplementation):
    _transform_id = "std.DICT"
    _signature = SarusSignature(
        SarusParameterMapping(
            name="elem",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        _, elems = await signature.collect()
        return dict(**elems)


class _slice(ExternalOpImplementation):
    _transform_id = "std.SLICE"
    _signature = SarusSignature(
        SarusParameter(
            name="start",
            annotation=Optional[int],
            default=None,
        ),
        SarusParameter(
            name="stop",
            annotation=int,
            default=-1,
        ),
        SarusParameter(
            name="step",
            annotation=Optional[int],
            default=None,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        (start, stop, step) = await signature.collect_args()
        return slice(start, stop, step)


class _set(ExternalOpImplementation):
    _transform_id = "std.SET"
    _signature = SarusSignature(
        SarusParameterArray(
            name="elem",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        elems = await signature.collect_args()
        return set(elems)


class _tuple(ExternalOpImplementation):
    _transform_id = "std.TUPLE"
    _signature = SarusSignature(
        SarusParameterArray(
            name="elem",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        elems = await signature.collect_args()
        return tuple(elems)


class keys(ExternalOpImplementation):
    _transform_id = "std.KEYS"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Dict,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        (this,) = await signature.collect_args()
        return list(this.keys())


class values(ExternalOpImplementation):
    _transform_id = "std.VALUES"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Dict,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        (this,) = await signature.collect_args()
        return list(this.values())


class sudo(ExternalOpImplementation):
    _transform_id = "std.SUDO"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=Any,
        ),
        name="sudo",
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        (this,) = await signature.collect_args()
        return this


class extend(ExternalOpImplementation):
    _transform_id = "std.EXTEND"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=List,
        ),
        SarusParameter(
            name="other",
            annotation=List,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        (this, other) = await signature.collect_args()
        this.extend(other)
        return this


class append(ExternalOpImplementation):
    _transform_id = "std.APPEND"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=List,
        ),
        SarusParameter(
            name="other",
            annotation=Any,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        (this, other) = await signature.collect_args()
        this.append(other)
        return this


class pop(ExternalOpImplementation):
    _transform_id = "std.POP"
    _signature = SarusSignature(
        SarusParameter(
            name="this",
            annotation=List,
        ),
        SarusParameter(
            name="index",
            annotation=int,
            default=-1,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        (this, index) = await signature.collect_args()
        return this.pop(index)
