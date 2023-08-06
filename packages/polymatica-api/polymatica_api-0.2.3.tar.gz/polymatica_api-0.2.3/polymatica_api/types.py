import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum


class _BaseEnum(Enum):
    def __str__(self):
        return self.value


class ColumnBaseType(int, _BaseEnum):
    String = 0
    Number = 1
    Date = 2
    Boolean = 3



class SortDirection(_BaseEnum):
    Asc = 'ASC'
    Desc = 'DESC'


class DataOptionBlockAggFn(_BaseEnum):
    Any = '-'
    Group = 'group'
    Sum = 'SUM'
    Min = 'MIN'
    Max = 'MAX'
    Average = 'AVG'
    First = 'LAST'
    Last = 'LAST'
    Count = 'COUNT'
    Distinct = 'DISTINCT'
    CountDistinct = 'COUNT_DISTINCT'


class DataOptionMethod(_BaseEnum):
    Aggregate = 'aggregate'
    Table = 'table'
    Pivot = 'pivot'


class FilterMethod(_BaseEnum):
    Equal = 'EQ'
    NotEqual = 'NEQ'
    GreaterThen = 'GT'
    LessThen = 'LT'
    GreaterThenOrEqual = 'GTE'
    LessThenOrEqual = 'LTE'
    InList = 'IN'
    NotInList = 'NIN'
    Like = 'LIKE'
    LikeCaseIgnore = 'LIKE_I'
    LikeNot = 'NLIKE'
    LikeNotCaseIgnore = 'NLIKE_I'
    StartsLike = 'START_LIKE'
    StartsLikeCaseIgnore = 'START_LIKE_I'
    StartsLikeNot = 'NSTART_LIKE'
    StartsLikeNotCaseIgnore = 'NSTART_LIKE_I'
    EndsLike = 'END_LIKE'
    EndsLikeCaseIgnore = 'END_LIKE_I'
    EndsLikeNot = 'NEND_LIKE'
    EndsLikeNotCaseIgnore = 'NEND_LIKE_I'
    DateRange = 'DATE_RANGE'
    DateRangeNot = 'NDATE_RANGE'



class CreateColumn(BaseModel):
    name: str
    path: str
    source_path: Optional[str]
    field_type: Optional[str]
    base_type: ColumnBaseType

    class Config:
        use_enum_values = True



class Column(BaseModel):
    id: int
    name: str
    field_type: str
    base_type: int
    path: str
    source_path: str
    update_date: datetime.datetime
    create_date: datetime.datetime


class Dataset(BaseModel):
    id: int
    name: str
    comment: str
    type: str
    columns: list[Column]


class DataColumn(BaseModel):
    key: str
    block_key: str
    column: Column


class Data(BaseModel):
    rows: List[Dict[str, Any]]
    columns: Optional[List[DataColumn]]
    dataset: Optional[Dataset]

    @property
    def column_map(self):
        result = dict()
        for item in self.columns:
            result[item.key] = item.column.name
        return result

    def get_path_by_name(self, name: str) -> Optional[str]:
        for item in self.columns or []:
            if item.column.name == name:
                return item.column.path
        return None

    def get_path_by_key(self, key: str) -> Optional[str]:
        for item in self.columns or []:
            if item.key == key:
                return item.column.path
        return None
