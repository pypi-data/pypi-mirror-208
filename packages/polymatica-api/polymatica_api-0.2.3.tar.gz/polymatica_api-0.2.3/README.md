This is a simple example of getting data from a server Polymatica Platform

```python
from polymatica_api import PolymaticaAPI
from polymatica_api.data_option import FilterAnd
from polymatica_api.types import DataOptionMethod, FilterMethod, SortDirection
import pandas as pd


p = PolymaticaAPI('{SERVER_URL}', 'Token {TOKEN}')
response = p.get_data([
    p.from_dataset('world_population.csv').
    method(DataOptionMethod.Aggregate).
    group("Country/Territory").
    sum(
        '2000 Population', 
        '2010 Population', 
        '2015 Population',
        '2020 Population',
        '2022 Population',
    ).
    sort("Country/Territory", SortDirection.Desc).
    sort("2010 Population", SortDirection.Desc).
    set_filter(
        FilterAnd("Country/Territory", FilterMethod.Equal, "Jamaica")
    )
])

data = response.get('default')
frame = pd.DataFrame(data.rows)
frame.rename(columns=data.column_map, inplace=True)
print(frame)
```