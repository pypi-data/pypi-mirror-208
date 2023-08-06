from functools import reduce
from typing import Iterable, Union

from pandas import DataFrame

from lumipy.lumiflex._table.operation import SetOperation, Select, Where
from lumipy.lumiflex._table.variable import TableLiteralVar
from lumipy.lumiflex.table import Table


def concat(sub_queries: Iterable[Union[Select, Where, SetOperation]]) -> SetOperation:
    """Vertically concatenate (union) a collection of subquery objects.

    Args:
        *sub_queries (Union[Select, Where, SetOperation]): subqueries to union together. Must be made only of select,
        where, and set operation (union, union all, exclude, intersect) statements.

    Returns:
        SetOperation: the union of all the subqueries.
    """
    return reduce(lambda x, y: x.union_all(y), sub_queries)


def from_pandas(df: DataFrame) -> Table:
    """Turn a pandas dataframe into a Luminesce SQL table variable that wraps a VALUES statement.

    Notes:
        Any nan values will be mapped to NULL. The character ' will be removed from all strings.

    Args:
        df (DataFrame): the dataframe to convert.

    Returns:
        Table: the corresponding table variable.

    """
    return TableLiteralVar(df=df).build()
