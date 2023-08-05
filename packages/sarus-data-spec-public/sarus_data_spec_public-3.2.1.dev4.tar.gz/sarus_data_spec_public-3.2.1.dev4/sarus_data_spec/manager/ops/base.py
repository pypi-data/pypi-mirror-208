from __future__ import annotations

import typing as t

import pyarrow as pa

from sarus_data_spec.manager.async_utils import decoupled_async_iter
import sarus_data_spec.dataspec_validator.typing as sdvt
import sarus_data_spec.typing as st


class DataspecStaticChecker:
    def __init__(self, dataspec: st.DataSpec):
        self.dataspec = dataspec

    def is_dp_applicable(self, public_context: t.Collection[str]) -> bool:
        """Statically check if a DP transform is applicable in this position.

        This verification is common to all dataspecs and is true if:
            - the dataspec is transformed and its transform has an equivalent
            DP transform
            - the DP transform's required PEP arguments are PEP and aligned
            (i.e. same PEP token)
            - other dataspecs arguments are public
        """
        return False

    def is_dp(self) -> bool:
        """Checks if the transform is DP and compatible with the arguments."""
        return False

    def dp_transform(self) -> t.Optional[st.Transform]:
        """Return the dataspec's DP equivalent transform if existing."""
        return None

    def dp_equivalent(self) -> t.Optional[st.Transform]:
        """Return the dataspec's DP equivalent transform if existing."""
        raise NotImplementedError

    async def private_queries(self) -> t.List[st.PrivateQuery]:
        """Return the PrivateQueries summarizing DP characteristics."""
        if self.is_dp():
            raise NotImplementedError
        else:
            return []


class DatasetStaticChecker(DataspecStaticChecker):
    def __init__(self, dataset: st.Dataset):
        super().__init__(dataset)
        self.dataset = dataset

    async def schema(self) -> st.Schema:
        """Computes the schema of the dataspec"""
        raise NotImplementedError

    def pep_token(self, public_context: t.Collection[str]) -> t.Optional[str]:
        """Return a token if the output is PEP."""
        raise NotImplementedError

    def pep_kind(self) -> sdvt.PEPKind:
        raise NotImplementedError


class DatasetImplementation:
    def __init__(self, dataset: st.Dataset):
        self.dataset = dataset

    async def to_arrow(
        self, batch_size: int
    ) -> t.AsyncIterator[pa.RecordBatch]:
        raise NotImplementedError

    async def size(self) -> st.Size:
        raise NotImplementedError

    async def multiplicity(self) -> st.Multiplicity:
        raise NotImplementedError

    async def bounds(self) -> st.Bounds:
        raise NotImplementedError

    async def marginals(self) -> st.Marginals:
        raise NotImplementedError

    async def sql(
        self,
        query: t.Union[str, t.Mapping[t.Union[str, t.Tuple[str, ...]], str]],
        dialect: t.Optional[st.SQLDialect] = None,
        batch_size: int = 10000,
    ) -> t.AsyncIterator[pa.RecordBatch]:
        """It composes the query and it sends it to the parent."""
        raise NotImplementedError

    @staticmethod
    async def decoupled_async_iter(
        source: t.AsyncIterator[pa.RecordBatch], buffer_size: int = 100
    ) -> t.AsyncIterator[pa.RecordBatch]:
        return decoupled_async_iter(source=source, buffer_size=buffer_size)


class ScalarImplementation:
    def __init__(self, scalar: st.Scalar):
        self.scalar = scalar

    async def value(self) -> t.Any:
        raise NotImplementedError

    @staticmethod
    async def decoupled_async_iter(
        source: t.AsyncIterator[pa.RecordBatch], buffer_size: int = 100
    ) -> t.AsyncIterator[pa.RecordBatch]:
        return decoupled_async_iter(source=source, buffer_size=buffer_size)
