import logging
import typing as t

import pyarrow as pa

from sarus_data_spec.arrow.type import type_from_arrow
from sarus_data_spec.manager.ops.processor.standard.standard_op import (  # noqa: E501
    StandardDatasetImplementation,
    StandardDatasetStaticChecker,
)
from sarus_data_spec.schema import schema
import sarus_data_spec.type as sdt
import sarus_data_spec.typing as st

logger = logging.getLogger(__name__)


class SelectSQLStaticChecker(StandardDatasetStaticChecker):
    def pep_token(self, public_context: t.Collection[str]) -> t.Optional[str]:
        return None

    async def schema(self) -> st.Schema:
        """With sqlalchemy is not possible to get type detection on text
        statement queries.
        https://github.com/sqlalchemy/sqlalchemy/issues/5677
        however, depending on the DBAPI used we can retrive its type descrption
        from the cursor. For those DBAPI not having this feature we are forced
        to execute the query and retrieve the schema from the results.

        Since the schema is public we may want to execute the query on the
        sythetic dataset.
        """
        select_sql_proto = self.dataset.transform().protobuf().spec.select_sql
        if select_sql_proto.query != '':
            parent_ds = t.cast(st.Dataset, self.parent(kind='dataset'))
            parent_schema = await self.parent_schema()
            logger.debug(
                f"Query {select_sql_proto.query} sent to the "
                f"parent dataset {parent_ds.uuid()} for the schema computation"
            )
            res = await parent_ds.manager().async_sql(
                dataset=parent_ds,
                query=select_sql_proto.query,
                dialect=t.cast(st.SQLDialect, select_sql_proto.sql_dialect),
            )
            table = pa.Table.from_batches(
                batches=[batch async for batch in res]
            )
            fields = {
                col: type_from_arrow(
                    arrow_type=table.field(col).type,
                    nullable=table.field(col).nullable,
                )
                for col in table.schema.names
            }
            schema_type = sdt.Struct(fields=fields)
            return schema(
                self.dataset,
                schema_type=schema_type,
                name=parent_schema.name(),
            )

        else:
            raise NotImplementedError(
                "SelectSQL is not implemented for a dict of queries"
            )


class SelectSQL(StandardDatasetImplementation):
    """Computes schema and arrow
    batches for a dataspec transformed by
    a select_sql transform
    """

    async def to_arrow(
        self, batch_size: int
    ) -> t.AsyncIterator[pa.RecordBatch]:
        select_sql_proto = self.dataset.transform().protobuf().spec.select_sql
        if select_sql_proto.query != '':
            parent_ds = t.cast(st.Dataset, self.parent(kind='dataset'))
            logger.debug(
                f"Query {select_sql_proto.query} sent to the "
                f"parent dataset {parent_ds.uuid()} for to arrow"
            )
            return await parent_ds.manager().async_sql(
                dataset=parent_ds,
                query=select_sql_proto.query,
                dialect=t.cast(st.SQLDialect, select_sql_proto.sql_dialect),
                batch_size=batch_size,
            )
        raise NotImplementedError(
            "SelectSQL is not implemented for a dict of queries"
        )

    # TODO
    # def sql_implementation(self) -> t.Optional[t.Dict[st.Path, str]]:
    #     query = self.dataset.transform().protobuf().spec.select_sql.query
    #     aliased_queries: t.Optional[t.Dict[st.Path, str]]
    #     if query == '':
    #         aliased_queries_proto = (
    #             self.dataset.transform()
    #             .protobuf()
    #             .spec.select_sql.aliased_queries
    #         )
    #         aliased_queries = {
    #             Path(alias_q.path): alias_q.query
    #             for alias_q in aliased_queries_proto.aliased_query
    #         }
    #     else:
    #         table_paths = self.dataset.schema().tables()
    #         assert len(table_paths) == 1
    #         aliased_queries = {table_paths[0]: query}
    #     return aliased_queries
