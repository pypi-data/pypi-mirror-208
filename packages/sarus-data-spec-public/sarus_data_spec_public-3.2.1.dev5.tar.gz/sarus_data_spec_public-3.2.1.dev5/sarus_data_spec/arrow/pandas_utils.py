import typing as t

import pyarrow as pa


def pandas_index_columns(schema: pa.Schema) -> t.List[str]:
    """Return the list of columns that have to be considered as Pandas index
    columns and ignored by the Sarus type.
    """
    pandas_metadata = schema.pandas_metadata
    if pandas_metadata is None:
        return []

    def column_name(index: t.Any) -> t.Optional[str]:
        if isinstance(index, str):
            return index
        elif isinstance(index, dict):
            return t.cast(t.Optional[str], index["name"])
        else:
            raise ValueError("Unrecognized Arrow `index_column` format")

    columns = [
        column_name(index) for index in pandas_metadata["index_columns"]
    ]
    return [col for col in columns if col is not None]


def remove_pandas_index_columns(table: pa.Table) -> pa.Table:
    """Remove pandas metadata and drop additional
    index columns used for Pandas indexing.
    """
    index_columns_names = pandas_index_columns(table.schema)
    return table.drop(index_columns_names).replace_schema_metadata(None)
