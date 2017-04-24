from dao.column import Column

class Table:
    def __init__(self, name, columns):
        self._name = name
        self._columns = [Column(name, dataType) for name, dataType in columns]

    @property
    def name(self):
        return self._name

    @property
    def columns(self):
        return self._columns