from arch_lint.dag import (
    DagMap,
)
from arch_lint.graph import (
    FullPathModule,
)
from fa_purity import (
    FrozenList,
)
from typing import (
    Dict,
    FrozenSet,
    TypeVar,
    Union,
)

_dag: Dict[str, FrozenList[Union[FrozenList[str], str]]] = {
    "redshift_client": (
        "schema",
        "table",
        "column",
        "data_type",
        "id_objs",
        "sql_client",
    ),
    "redshift_client.sql_client": (
        ("connection", "query"),
        "_assert",
        "primitive",
    ),
    "redshift_client.schema": (
        "client",
        "core",
    ),
    "redshift_client.table": (
        "client",
        "core",
        "_assert",
    ),
    "redshift_client.data_type": (
        "decode",
        "alias",
        "core",
    ),
}
_T = TypeVar("_T")


def raise_or_return(item: Union[Exception, _T]) -> _T:
    if isinstance(item, Exception):
        raise item
    return item


def project_dag() -> DagMap:
    return raise_or_return(DagMap.new(_dag))


def forbidden_allowlist() -> Dict[FullPathModule, FrozenSet[FullPathModule]]:
    _raw: Dict[str, FrozenSet[str]] = {
        "psycopg2": frozenset(
            [
                "redshift_client.sql_client",
                "redshift_client.sql_client.query",
                "redshift_client.sql_client.connection",
            ]
        ),
    }
    return {
        raise_or_return(FullPathModule.from_raw(k)): frozenset(
            raise_or_return(FullPathModule.from_raw(i)) for i in v
        )
        for k, v in _raw.items()
    }
