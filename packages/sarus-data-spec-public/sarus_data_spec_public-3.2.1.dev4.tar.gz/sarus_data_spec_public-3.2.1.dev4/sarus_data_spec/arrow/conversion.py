import typing as t

import pandas as pd
import pyarrow as pa

from sarus_data_spec.manager.async_utils import (
    sync_iterator_from_async_iterator,
)
import sarus_data_spec.typing as st

NO_SERIES_NAME = "__sarus_no_name__"


async def async_cast_arrow_batches(
    batches_async_iterator: t.AsyncIterator[pa.RecordBatch],
    kind: st.DatasetCastable,
) -> st.DatasetCastable:
    """Convert an async record batches iterator to another Python type."""
    if kind not in t.get_args(st.DatasetCastable):
        raise TypeError(f"Cannot cast a Dataset to type {kind}")

    if kind == t.Iterator[pa.RecordBatch]:
        return sync_iterator_from_async_iterator(batches_async_iterator)
    if kind == pd.DataFrame:
        return await async_arrow_batches_to_dataframe(batches_async_iterator)
    elif kind == pd.Series:
        return await async_arrow_batches_to_series(batches_async_iterator)
    else:
        raise NotImplementedError(
            f"Arrow to Python: No converter implemented for type {kind}"
        )


async def async_arrow_batches_to_dataframe(
    batches_async_iterator: t.AsyncIterator[pa.RecordBatch],
) -> pd.DataFrame:
    arrow_batches = [batch async for batch in batches_async_iterator]
    # follow advices in
    # https://arrow.apache.org/docs/python/pandas.html#reducing
    # -memory-use-in-table-to-pandas
    tab = pa.Table.from_batches(arrow_batches)
    df = tab.to_pandas(split_blocks=False, self_destruct=True)
    del tab  # not necessary, but a good practice
    return df


async def async_arrow_batches_to_series(
    batches_async_iterator: t.AsyncIterator[pa.RecordBatch],
) -> pd.Series:
    """Returns the first columns of the DataFrame."""
    df = await async_arrow_batches_to_dataframe(batches_async_iterator)
    first_col = df.columns[0]
    series = df[first_col]
    if first_col == NO_SERIES_NAME:
        # This is a default value for a column.
        # The series actually has no name.
        series.name = None
    return series


def to_pyarrow_table(data: t.Any) -> pa.Table:
    """Convert the result of an external transform to a Pyarrow Table."""
    if not type(data) in t.get_args(st.DatasetCastable):
        raise TypeError(f"Cannot convert {type(data)} to Arrow batches.")

    if isinstance(data, pd.DataFrame):
        df = t.cast(pd.DataFrame, data)
        return pa.Table.from_pandas(df)
    elif isinstance(data, pd.Series):
        sr = t.cast(pd.Series, data)
        if sr.name is None:
            # We need to set a name otherwise pandas adds a default one.
            sr.name = NO_SERIES_NAME
        return pa.Table.from_pandas(pd.DataFrame(sr))
    elif isinstance(data, t.Iterator):
        # We test this case last because DataFrames and Series are also
        # Iterators. We cannot easily test that an object is an Iterator of a
        # specific type. So we put the Iterator[pa.RecordBatch] last as the
        # last possible case.
        batches = t.cast(t.Iterator[pa.RecordBatch], data)
        return pa.Table.from_batches(batches)
    else:
        raise NotImplementedError(
            f"Python to Arrow: No converter implemented for type {type(data)}"
        )
