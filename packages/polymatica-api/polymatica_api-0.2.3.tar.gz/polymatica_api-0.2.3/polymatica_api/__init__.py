from .types import Dataset, Data, CreateColumn
from .data_option import DataOption

import typing
import requests
import urllib.parse


HOST_ROUTE = dict(
    dataset='/proxy/manager/api/v1/dataset',
    data_dataset='/proxy/manager/api/v1/data/dataset',
    write_line='/proxy/manager/api/v1/data-line/{id}',
    write_lines='/proxy/manager/api/v1/data-line/{id}/rows',
    delete_line='/proxy/manager/api/v1/data-line/{id}/{uid}',
    update_line='/proxy/manager/api/v1/data-line/{id}/{uid}',
    dataset_create='/proxy/manager/api/v1/dataset-local'
)


class PolymaticaAPI:
    _host: str
    _session: requests.Session

    def __init__(self, host, token):
        self._host = host
        self._session = requests.session()
        self._session.headers = {
            "Authorization": token
        }

    def from_dataset(self, name) -> DataOption:
        return DataOption(name, self)

    def delete_line(self, dataset_id: int, line_id: str):
        return self._session.delete(self.route('delete_line').format(id=dataset_id, uid=line_id)).json()

    def update_line(self, dataset_id: int, line_id: str, row: typing.Dict):
        return self._session.put(self.route('update_line').format(id=dataset_id, uid=line_id), json=row).json()

    def write_line(self, dataset_id: int, row: typing.Dict):
        return self._session.post(self.route('write_line').format(id=dataset_id), json=row).json()

    def write_lines(self, dataset_id: int, rows: typing.List[typing.Dict]):
        return self._session.post(self.route('write_lines').format(id=dataset_id), json=rows).json()

    def get_dataset(self, name) -> typing.Optional[Dataset]:
        data = self._session.get(self.route('dataset'), params=dict(
            name=name
        )).json()

        for item in data.get('rows'):
            dataset = Dataset.parse_obj(item)
            if dataset.name == name:
                return dataset
        return None

    def get_data(self, options, get_columns: bool = True, get_dataset: bool = False) -> typing.Dict[str, Data]:
        data = self._session.post(self.route('data_dataset'), json=dict(
            data_options=list(map(lambda item: item.make(), options)),
            get_columns=get_columns,
            get_dataset=get_dataset
        )).json()

        result = dict()
        for key in data:
            result[key] = Data.parse_obj(data[key])

        return result

    def create_dataset(self, name: str, columns: typing.List[CreateColumn], descriotion: str=''):
        data = self._session.post(self.route('dataset_create'), json=dict(
            name=name,
            descriotion=descriotion,
            columns=list(map(lambda item: item.dict(), columns))
        )).json()

        id = data.get('id')

        if not id:
            raise Exception(data)
        return data

    def route(self, name: str) -> str:
        if name not in HOST_ROUTE:
            raise Exception(f'Route "{name}" not found')
        return urllib.parse.urljoin(self._host, HOST_ROUTE[name])