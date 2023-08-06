# py-bigquery-mock
pip install py-bigquery-mock

```python

import bigquery_mock.bigquery_mock as Mock

class Client(Mock.Client):

    def __init__(self):
        data = [
                [('key', 'value')
                    ]
                ]
        super().__init__(data)


bigquery_client = Client()
sql = "Any string, since we are mocking"
results = bigquery_client.query( sql)  
for i in results:
    #any BQ methods should work
    print(i.items())

```
