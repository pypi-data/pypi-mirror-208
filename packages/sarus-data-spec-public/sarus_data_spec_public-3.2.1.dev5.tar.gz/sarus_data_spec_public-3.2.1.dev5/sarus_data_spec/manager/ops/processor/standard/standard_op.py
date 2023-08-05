import hashlib
import logging
import typing as t
import warnings

import numpy as np
import pyarrow as pa

from sarus_data_spec.dataset import Dataset
from sarus_data_spec.manager.ops.base import (
    DatasetImplementation,
    DatasetStaticChecker,
    DataspecStaticChecker,
    ScalarImplementation,
)

try:
    from sarus_data_spec.manager.ops.sql_utils.table_mapping import (
        name_encoder,
        table_mapping,
    )
except ModuleNotFoundError:
    warnings.warn('table_mapping not found. Cannot send sql queries.')
from sarus_data_spec.scalar import Scalar
import sarus_data_spec.typing as st

try:
    from sarus_sql import ast_utils, rename_tables
except ModuleNotFoundError:
    warnings.warn(
        'sarus-sql not found, can\'t parse, translate and' ' rewrite queries'
    )


logger = logging.getLogger(__name__)


class StandardDatasetStaticChecker(DatasetStaticChecker):
    def parent(self, kind: str = 'dataset') -> t.Union[st.Dataset, st.Scalar]:
        return parent(self.dataset, kind=kind)

    async def parent_schema(self) -> st.Schema:
        parent = self.parent(kind='dataset')
        assert isinstance(parent, Dataset)
        return await parent.manager().async_schema(parent)

    async def parent_marginals(self) -> st.Marginals:
        parent = self.parent(kind='dataset')
        assert isinstance(parent, Dataset)
        return await parent.manager().async_marginals(parent)

    def pep_token(self, public_context: t.Collection[str]) -> t.Optional[str]:
        """By default we implement that the transform inherits the PEP status
        but changes the PEP token."""
        parent_token = self.parent().pep_token()
        if parent_token is None:
            return None

        transform = self.dataset.transform()
        h = hashlib.md5()
        h.update(parent_token.encode("ascii"))
        h.update(transform.protobuf().SerializeToString())

        return h.hexdigest()


class StandardDatasetImplementation(DatasetImplementation):
    """Object that executes first routing among ops between
    transformed/source and processor
    """

    def parents(self) -> t.List[st.DataSpec]:
        return parents(self.dataset)

    def parent(self, kind: str = 'dataset') -> t.Union[st.Dataset, st.Scalar]:
        return parent(self.dataset, kind=kind)

    async def parent_to_arrow(
        self, batch_size: int = 10000
    ) -> t.AsyncIterator[pa.RecordBatch]:
        parent = self.parent(kind='dataset')
        assert isinstance(parent, Dataset)
        parent_iterator = await parent.manager().async_to_arrow(
            parent, batch_size=batch_size
        )
        return await self.decoupled_async_iter(parent_iterator)

    async def parent_schema(self) -> st.Schema:
        parent = self.parent(kind='dataset')
        assert isinstance(parent, Dataset)
        return await parent.manager().async_schema(parent)

    async def parent_value(self) -> t.Any:
        parent = self.parent(kind='scalar')
        assert isinstance(parent, Scalar)
        return await parent.manager().async_value(parent)

    async def parent_size(self) -> st.Size:
        parent = self.parent(kind='dataset')
        assert isinstance(parent, Dataset)
        return await parent.manager().async_size(parent)

    async def parent_multiplicity(self) -> st.Multiplicity:
        parent = self.parent(kind='dataset')
        assert isinstance(parent, Dataset)
        return await parent.manager().async_multiplicity(parent)

    async def parent_bounds(self) -> st.Bounds:
        parent = self.parent(kind='dataset')
        assert isinstance(parent, Dataset)
        return await parent.manager().async_bounds(parent)

    async def parent_marginals(self) -> st.Marginals:
        parent = self.parent(kind='dataset')
        assert isinstance(parent, Dataset)
        return await parent.manager().async_marginals(parent)

    async def ensure_batch_correct(
        self,
        async_iterator: t.AsyncIterator[pa.RecordBatch],
        func_to_apply: t.Callable,
        batch_size: int,
    ) -> t.AsyncIterator[pa.RecordBatch]:
        """Method that executes func_to_apply on each batch
        of the async_iterator but rather than directly returning
        the result, it accumulates them and returns them progressively
        so that each new batch has batch_size."""

        global_array = None
        async for batch in async_iterator:
            new_array = await func_to_apply(batch)
            if len(new_array) == batch_size and global_array is None:
                yield pa.RecordBatch.from_struct_array(
                    new_array.take(
                        np.linspace(0, batch_size - 1, batch_size, dtype=int)
                    )
                )
            elif global_array is not None:
                global_array = pa.concat_arrays([global_array, new_array])
                if len(global_array) < batch_size:
                    continue
                else:
                    # here cannot use array.slice because there
                    # is a bug in the columns being copied
                    # when we switch to record batch
                    yield pa.RecordBatch.from_struct_array(
                        global_array.take(
                            np.linspace(
                                0, batch_size - 1, batch_size, dtype=int
                            )
                        )
                    )
                    global_array = global_array.take(
                        np.linspace(
                            batch_size,
                            len(global_array) - 1,
                            len(global_array) - batch_size,
                            dtype=int,
                        )
                    )

            else:
                # initialize global_array
                global_array = new_array
                continue
        # handle remaining array: split it in

        if global_array is not None and len(global_array) > 0:
            while len(global_array) > 0:
                min_val = min(batch_size, len(global_array))
                indices = np.linspace(
                    0, len(global_array) - 1, len(global_array), dtype=int
                )
                yield pa.RecordBatch.from_struct_array(
                    global_array.take(indices[:min_val])
                )
                global_array = global_array.take(indices[min_val:])

    def sql_implementation(self) -> t.Optional[t.Dict[st.Path, str]]:
        """Returns a dict of queries equivalent to the current transform.
        If the the transform does not change the schema, then return None"""
        raise NotImplementedError(
            "No SQL implementation for dataset issued from"
            f" {self.dataset.transform().spec()} transform."
        )

    async def sql(
        self,
        query: t.Union[str, t.Mapping[t.Union[str, t.Tuple[str, ...]], str]],
        dialect: t.Optional[st.SQLDialect] = None,
        batch_size: int = 10000,
    ) -> t.AsyncIterator[pa.RecordBatch]:
        """It rewrites and/or composes the query and sends it to the parent."""
        transfo_queries = self.sql_implementation()
        current_schema = await self.dataset.manager().async_schema(
            self.dataset
        )
        parent_schema = await self.parent_schema()
        if transfo_queries is None:
            if current_schema.name() == parent_schema.name():
                parent_query = query
            else:
                table_map = table_mapping(
                    tables=current_schema.tables(),
                    sarus_schema_name=current_schema.name(),
                )

                parent_query = rename_tables.rename_tables(
                    t.cast(str, query),
                    t.cast(t.Dict[st.Path, t.Tuple[str]], table_map),
                )
        else:
            transfo_renamed = {
                name_encoder(
                    names=tuple(tab_name.to_strings_list()[0]),
                    length=10,
                ): query_str
                for tab_name, query_str in transfo_queries.items()
            }
            parent_query = ast_utils.compose_query(
                transfo_renamed, t.cast(str, query)
            )
        parent_ds = t.cast(st.Dataset, self.parent(kind='dataset'))
        logger.debug(
            f"query {parent_query} sent to the "
            f"parent dataset {parent_ds.uuid()}"
        )
        return await parent_ds.manager().async_sql(
            dataset=parent_ds,
            query=parent_query,
            dialect=dialect,
            batch_size=batch_size,
        )


class StandardScalarStaticChecker(DataspecStaticChecker):
    ...


class StandardScalarImplementation(ScalarImplementation):
    def parent(self, kind: str = 'dataset') -> st.DataSpec:
        return parent(self.scalar, kind=kind)

    def parents(self) -> t.List[st.DataSpec]:
        return parents(self.scalar)

    async def parent_to_arrow(
        self, batch_size: int = 10000
    ) -> t.AsyncIterator[pa.RecordBatch]:
        parent = self.parent(kind='dataset')
        assert isinstance(parent, Dataset)
        parent_iterator = await parent.manager().async_to_arrow(
            parent, batch_size=batch_size
        )
        return await self.decoupled_async_iter(parent_iterator)

    async def parent_schema(self) -> st.Schema:
        parent = self.parent(kind='dataset')
        assert isinstance(parent, Dataset)
        return await parent.manager().async_schema(parent)

    async def parent_value(self) -> t.Any:
        parent = self.parent(kind='scalar')
        assert isinstance(parent, Scalar)
        return await parent.manager().async_value(parent)


def parent(dataspec: st.DataSpec, kind: str) -> t.Union[st.Dataset, st.Scalar]:
    pars = parents(dataspec)
    if kind == 'dataset':
        parent: t.Union[t.List[Scalar], t.List[Dataset]] = [
            element for element in pars if isinstance(element, Dataset)
        ]
    else:
        parent = [element for element in pars if isinstance(element, Scalar)]
    assert len(parent) == 1
    return parent[0]


def parents(dataspec: st.DataSpec) -> t.List[st.DataSpec]:
    parents_args, parents_kwargs = dataspec.parents()
    parents_args.extend(parents_kwargs.values())
    return parents_args
