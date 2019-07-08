"""Table entry with his own related records"""

from models import SQLInsertRequest


class TableEntry():
    """Structure of new entry record with own relations records"""

    def __init__(self, target):

        self._sql = SQLInsertRequest()
        self._master = target
        self._request = self._sql.table(target, "script")
        self._fields = self._sql.table(target, "fields")
        self._has_many = self._sql.table(target, "has_many")
        self._has_one = self._sql.table(target, "has_one")
        for has in self._has_many:
            has["entry"] = TableEntry(has["table"])
        for has in self._has_one:
            has["entry"] = TableEntry(has["table"])

    def __repr__(self):
        return self._master

    def __str__(self):
        return self._master

    @property
    def request(self):
        """Property to get request of entry table"""

        return self._request

    @property
    def fields(self):
        """Property to get fields"""

        return self._fields

    @property
    def has_many(self):
        """Property to get has_many relations list"""

        return self._has_many

    @property
    def has_one(self):
        """Property to get has_one relations list"""

        return self._has_one

    def find_relation(self, table, has_many=False):
        """return relation target by table name and type of relation"""

        relations  = self._has_one \
            if not has_many \
            else self._has_many
        for relation in relations:
            if relation["table"] == table:
                return relation
        return None
