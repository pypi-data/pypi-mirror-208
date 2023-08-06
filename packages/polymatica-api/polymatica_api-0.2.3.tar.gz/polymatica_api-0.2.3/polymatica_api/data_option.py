from .types import Column, DataOptionBlockAggFn, DataOptionMethod, FilterMethod, SortDirection
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class _DataOptionBlock(BaseModel):
    block_name: str
    column_name: str
    agg_fn: DataOptionBlockAggFn


class _Sort:
    def __init__(self, column: str, direction: SortDirection):
        self._column = column
        self._direction = direction

    def make(self, column_by_name: Dict[str, Column]) -> Optional[Dict]:
        if self._column not in column_by_name:
            return None
        return dict(
            column_id=column_by_name[self._column].id,
            direction=str(self._direction)
        )


class _Filter:
    def __init__(self, column: str, method: FilterMethod, value: Any):
        self._column = column
        self._method = method
        self._value = value

    def _make(self, logical: str, column_by_name: Dict[str, Column]) -> Optional[Dict]:
        if self._column not in column_by_name:
            return None
        return dict(
            logical=logical,
            column_id=column_by_name[self._column].id,
            action=str(self._method),
            value=self._value,
        )


class FilterAnd(_Filter):
    def make(self, column_by_name: Dict[str, Column]) -> Optional[Dict]:
        return super()._make("AND", column_by_name)


class FilterOr(_Filter):
    def make(self, column_by_name: Dict[str, Column]) -> Optional[Dict]:
        return super()._make("OR", column_by_name)


class DataOption:
    def __init__(self, name: str, api):
        self._api = api
        self._name = name
        self._key = "default"
        self._method: DataOptionMethod = DataOptionMethod.Table
        self._sort: List[_Sort] = []
        self._filters: List[FilterAnd | FilterOr] = []
        self._offset = 0
        self._limit = 1000
        self._blocks: List[_DataOptionBlock] = []

    def offset(self, value: int):
        self._offset = value
        return self

    def limit(self, value: int):
        self._limit = value
        return self

    def key(self, name: str):
        self._key = name
        return self

    def method(self, name: DataOptionMethod):
        self._method = name
        return self

    def set_filter(self, *filters: FilterAnd | FilterOr):
        for item in filters:
            self._filters.append(item)
        return self

    def sort(self, name, direction: SortDirection = SortDirection.Asc):
        self._sort.append(_Sort(name, direction))
        return self

    def select(self, *name: str):
        self.add_columns('default', name, DataOptionBlockAggFn.Any)
        return self

    def group(self, *name: str):
        self.add_columns('default', name, DataOptionBlockAggFn.Group)
        return self

    def sum(self, *name: str):
        self.add_columns('default', name, DataOptionBlockAggFn.Sum)
        return self

    def min(self, *name: str):
        self.add_columns('default', name, DataOptionBlockAggFn.Min)
        return self

    def max(self, *name: str):
        self.add_columns('default', name, DataOptionBlockAggFn.Max)
        return self

    def avg(self, *name: str):
        self.add_columns('default', name, DataOptionBlockAggFn.Average)
        return self

    def first(self, *name: str):
        self.add_columns('default', name, DataOptionBlockAggFn.First)
        return self

    def last(self, *name: str):
        self.add_columns('default', name, DataOptionBlockAggFn.Last)
        return self

    def count(self, *name: str):
        self.add_columns('default', name, DataOptionBlockAggFn.Count)
        return self

    def distinct(self, *name: str):
        self.add_columns('default', name, DataOptionBlockAggFn.Distinct)
        return self

    def count_distinct(self, *name: str):
        self.add_columns('default', name, DataOptionBlockAggFn.CountDistinct)
        return self

    def add_columns(self, block_name: str, names: List[str], agg_fn: DataOptionBlockAggFn):
        for item in names:
            self._blocks.append(
                _DataOptionBlock(
                    block_name=block_name,
                    column_name=item,
                    agg_fn=agg_fn,
                )
            )
        return self

    def make(self) -> dict:
        dataset = self._api.get_dataset(self._name)
        filters = []
        sort = []

        if not dataset:
            raise Exception(f'Dataset "{self._name}" not found')

        columns_by_name: Dict[str, Column] = dict()
        for item in dataset.columns:
            columns_by_name[item.name] = item

        for item in self._filters:
            item = item.make(columns_by_name)
            if item:
                filters.append(item)

        for item in self._sort:
            item = item.make(columns_by_name)
            if item:
                sort.append(item)

        blocks_by_key = dict()
        for item in self._blocks:
            if item.block_name not in blocks_by_key:
                blocks_by_key[item.block_name] = dict(
                    key=item.block_name,
                    columns=[]
                )

            block_columns = blocks_by_key[item.block_name].get('columns')

            column = columns_by_name.get(item.column_name)
            if not column:
                raise Exception(f'Column "{item.column_name}" not found')

            block_columns.append(dict(
                agg_fn=str(item.agg_fn),
                column_id=column.id
            ))

        return dict(
            key=self._key,
            method=str(self._method),
            sort=sort,
            filters=filters,
            blocks=list(blocks_by_key.values()),
            dataset_id=dataset.id,
            offset=self._offset,
            limit=self._limit,
        )
