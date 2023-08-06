from dataclasses import dataclass
from typing import Optional, Type
from dbt.adapters.base import BaseRelation
from dbt.dataclass_schema import StrEnum
from dbt.utils import classproperty


class UpsolverRelationType(StrEnum):
    # Built-in materialization types.
    External = "external"
    Table = "table"
    # Upsolver-specific materialization types.
    Incremental = "incremental"
    Connection = "connection"
    MaterializedView = "materializedview"

@dataclass(frozen=True, eq=False, repr=False)
class UpsolverRelation(BaseRelation):
    type: Optional[UpsolverRelationType] = None

    @classproperty
    def get_relation_type(cls) -> Type[UpsolverRelationType]:
        return UpsolverRelationType
