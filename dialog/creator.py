"""Create records"""

import re
from pathlib import Path
from PIL import Image

from pg_manager import SQLInsertRequest, SQLShowRequest, Database
from models import TableEntry, Field
from tools import Convert


class Creator:
    """Create records"""

    YES = re.compile(r'o|y|oui|yes', re.IGNORECASE)
    ADD_A = re.compile(r'^(.*ajouter un[e]? )(.*)$', re.IGNORECASE)

    def __init__(self, target):

        self._sql = SQLInsertRequest()
        self._db = Database()
        self._convert = Convert()
        self._messages = ""
        self._relational_values = []
        self._entry = TableEntry(target)
        self._field = Field()

    @property
    def entry(self):
        """Property entry"""

        return self._entry

    @property
    def messages(self):
        """Property for get messages status"""

        return self._messages

    def record_from_file(self, target, file, type_file):
        """Record data from file content list of entries"""

        if type_file == "csv":
            char_separator = input("Quelle est le caractère de "
                                   "séparation du fichier CSV svp ? ")
            PCG = []
            with open(file, 'r') as pcg:
                for line in pcg:
                    PCG.append(tuple(line.strip().split(char_separator)))
            request = self._sql.table(target, "script")
            for pcg_values in PCG:
                id = self._db.request(request, pcg_values, ask=True)
                self._messages += f"Nouvelle enregistrement dans la table " \
                    f"{target}  à l'id: {id[0]}\n"

    def _create_simple(self, entry):
        """ask for fields entry and record, then return id"""

        id = []
        while not id:
            values = self._get_fields_values_for(entry.fields)
            request = self._sql.table(str(entry), "script")
            id = self._db.request(request, tuple(values), ask=True)
        return int(id[0][0])

    def _record_through(self, through, values):
        """Record relational table"""

        request = self._sql.table(through, "script")
        print(request, values)
        success = self._db.request(request, tuple(values))
        return success

    def _get_maybe_existing_record(self, relation) -> (str, int):
        """Return message and id for new or existing table record"""

        message = None
        id = 0
        if relation["exist"]:
            choices = self._show_existing_records(
                relation["table"], relation["show"], relation["exist"])
            answer = input("Faites un choix: ")
            if relation["exist"] == "maybe" and answer==choices[-1]:
                message, id = self._new_table_record(relation["entry"])
            elif answer != "0":
                id = choices[int(answer)]
                message = f"Valeur de relation choisie: " \
                    f"{relation['table']}, id: {id}\n"
        return message, id

    def _show_existing_records(self, table, field, exist):
        """Print enumerated list of fields 'field' existing 'table' records
            and return a list of id and 'n': [id,.....,'n']"""

        choices = ["STOP"]
        print("  0) -- STOP --")
        sql = SQLShowRequest()
        sub_request = sql.table(table)
        request = re.sub(r'\*', f"id, {field}", sub_request)
        records = self._db.request(request, ask=True)
        for n, record in enumerate(records):
            choices.append(int(record[0]))
            string = "%3s) %s" % (n+1, record[1])
            print(string)
        if exist == "maybe":
            choices.append("n")
            print("  n) -- Créer --")
        return choices

    def _get_required_(self, through, what=None) -> list:
        """Return required tables from relational table name 'through'"""

        script = self._sql.table(through)["script"]
        fk = lambda x: re.match(r'.*_id', x, re.IGNORECASE)
        sub_id = lambda x: re.sub('_id', '', x)
        fields = re.match(r'.*\((.*)\) VALUES.*', script).group(1).split(", ")
        if what == "fk":
            return list(filter(fk, fields))
        if what == "tables":
            return list(map(sub_id, list(filter(fk, fields))))
        return fields

    def _get_fields_values_for(self, fields) -> list:
        """Return values list for fields required"""

        values = list()
        for field in fields:
            value = None
            if field["type"] == "varchar":
                if field["test"] == "file":
                    value = self._field.file_(field)
                elif field["test"] == "image":
                    value = self._field.image_(field)
                else:
                    value = self._field.varchar_(field)
            if field["type"] == "int":
                value = self._field.int_(field)
            if field["type"] == "enum":
                value = self._field.enum_(field)
            if field["type"] == "bytea":
                value = self._field.bytea_(field, values)
            if field["type"] == "bool":
                value = self._field.bool_(field)
            if field["type"] == "date":
                value = self._field.date_(field)
            values.append(value)

        return values

    @staticmethod
    def _get_an_other(string) -> str:
        """Add 'autre ' inside string at precise point"""

        match = Creator.ADD_A.match(string)
        question = match.group(1) + "autre " + match.group(2)
        return question
