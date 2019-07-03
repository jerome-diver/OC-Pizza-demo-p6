"""Read content of tables"""

from pg_manager import Database, SQLShowRequest

import re
from cli_helpers.tabular_output import TabularOutputFormatter


class Reader:
    """Read records from tables"""

    MATCH_MEMORY = re.compile(r'^<memory at .*>')

    def __init__(self, table, inline=False):

        self._table = table
        self._inline = inline
        self._message = ""
        self._request = None
        self._sql = SQLShowRequest()
        self._db = Database()
        self.create_request(table)

    def create_request(self, table):
        """show from SQL SELECT statement for table"""

        self._request = self._sql.table(table)

    def conditions(self, condition):
        """Add conditions to SQL request"""

        self._request += f"WHERE {condition}"

    @property
    def message(self):
        """Property message reader"""

        formatter = TabularOutputFormatter(format_name="simple")
        self._message = f"===  Liste des enregistrements de la " \
                        f"table '{self._table}'  ===\n\n"
        headers, *records = self._db.request(self._request,
                                             ask=True,
                                             with_headers=True)
        if self._inline:
            for n, record in enumerate(records):
                line = f"== resultat => enregistrement {n + 1}: =>\n"
                for i, field in enumerate(record):
                    if Reader.MATCH_MEMORY.match(str(field)):
                        field = "-byte data-"
                    line += "\t%-12s: %s \n" % (headers[i],str(field))
                self._message += line + "\n"
        else:
            for x in formatter.format_output(records, headers):
                self._message += x + "\n"
        return self._message
