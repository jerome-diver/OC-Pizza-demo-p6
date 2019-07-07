"""Inspect content of database (not READ records)"""

from pg_manager import Database
from models import SQLShowRequest
from cli_helpers.tabular_output import TabularOutputFormatter


class Inspector():

    def __init__(self):

        self._sql = SQLShowRequest()
        self._db = Database()

    def tables(self) -> str:
        """Show tables of database 'oc-pizza'"""

        request = self._sql.list()
        string = "========================================================\n"
        string += "=============  Tables list of 'oc-pizza':  =============\n"
        string += "========================================================\n"
        string += "request: %s \n" % request
        records = self._db.request(request, ask=True)
        for record in records:
            string +=  record[0] + "\n"
        return string

    def table(self, name):
        """Show name and type of fields for table 'name'"""

        string = "========================================================\n"
        string += "=========  Table  %-24s :  ==========\n" % name
        string += "========================================================\n"
        formatter = TabularOutputFormatter(format_name="simple")
        request = self._sql.columns()
        records = self._db.request(request, (name,), ask=True)
        headers = ["Name", "Default", "Nullable", "Type"]
        for x in formatter.format_output(records, headers):
            string += x + "\n"
        return string

    def types(self):
        """Show types list and values"""

        string = "========================================================\n"
        string += "======================  Types   =======================\n"
        string += "========================================================\n"
        formatter = TabularOutputFormatter(format_name="simple")
        request = self._sql.types()
        records = self._db.request(request, ask=True)
        data = list()
        for record in records:
            data.append(record[1:3])
        headers = ["Name", "Enums values"]
        for x in formatter.format_output(data, headers):
            string += x + "\n"
        return string

    def type(self, target, return_values=False):
        """Show Type for target or return values only
        (if return_values=True)"""

        string = "========================================================\n"
        string += "================  Type %-12s  =================\n" % target
        string += "========================================================\n"
        formatter = TabularOutputFormatter(format_name="simple")
        request = self._sql.type(target)
        records = self._db.request(request, ask=True)
        data = list()
        for record in records:
            data.append(record[1:3])
