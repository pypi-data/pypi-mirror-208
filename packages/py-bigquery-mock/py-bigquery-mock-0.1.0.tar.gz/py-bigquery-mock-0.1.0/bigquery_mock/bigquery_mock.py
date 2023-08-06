class SchemaField:

    def __init__(self):
        self.field_type = None

class RowIterator:

    def __init__(self, data):
        self.counter = 0
        self.total_rows = len(data)
        self.data = data
        self.schema = [SchemaField()]

    def __iter__(self):
        return self

    def __next__(self):
        if self.counter< self.total_rows:
            self.counter += 1
            return Row(row = self.data[self.counter -1])
        else:
            raise StopIteration

    def result(self):
        return self

class Row():

    def __init__(self, row):
        self.info = {}
        self.row = row

    def get(self, *args, **kwargs):
        if args:
            return self.info.get(args)
        return self.info.get(kwargs['key'])

    def items(self, *args, **kwargs):
        for i in self.row:
            yield i

    def values(self, *args, **kwargs):
        return (),

    def keys(self, *args, **kwargs):
        return {}.keys()

class Result():

    def __init__(self, data):
        assert False, 'not used'
        self.data = data

    def result(self):
        return RowIterator(data = self.data)

class Query:

    def __init__(self, data):
        self.data = data

class BigQueryMock:

    def __init__(self, data = None):
        self.data = data

    def query(self, *args, **kwargs):
        return RowIterator(data = self.data)

