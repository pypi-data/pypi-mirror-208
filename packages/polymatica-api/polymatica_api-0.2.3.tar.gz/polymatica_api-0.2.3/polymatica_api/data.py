from .types import Column, Dataset
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class DataColumn(BaseModel):
    key: str
    block_key: str
    column: Column


class Data(BaseModel):
    rows: List[Dict[str, Any]]
    columns: Optional[List[DataColumn]]
    dataset: Optional[Dataset]
