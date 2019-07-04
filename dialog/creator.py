"""Create records"""

import re
from pathlib import Path
from PIL import Image

from pg_manager import SQLInsertRequest, SQLShowRequest, Database
from models import TableEntry
from tools import Convert


class Creator:
    """Create records"""

    YES = re.compile(r'o|y|oui|yes', re.IGNORECASE)

    def __init__(self, target, file=None, type_file=None):

        self._sql = SQLInsertRequest()
        self._db = Database()
        self._convert = Convert()
        self._messages = ""
        self._relational_values = []
        self._entry = TableEntry(target)
        if not file:
            self.record()
        else:
            self.record_from_file(target, file, type_file)

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

    def record(self):
        """Create user record"""

        message, id = self._new_table_record(self._entry)
        self._messages += message
        if self._entry.has_many:
            message = self._collect_many_relations(self._entry.has_many)
            self._messages += message
            message = self._record_has_many_links(id)
            self._messages += message

    def _new_table_record(self, entry) -> (str, int):
        """Record new table from fields"""

        id = None
        message = ""
        while not id:
            values = self._get_fields_values_for(entry.fields)
            if entry.has_one:
                for has_one in entry.has_one:
                    if has_one["exist"]:
                        ho_message, ho_id = self._get_maybe_existing_record(
                            has_one)
                    else:
                        ho_message, ho_id = self._new_table_record(
                            has_one["entry"])
                    message += ho_message
                    values.append(ho_id)
            id = self._db.request(entry.request, tuple(values),
                                  ask=True)[0][0]
        message += f"Ajout de l'enregistrement "\
                  f"dans la table: '{str(entry)}' "\
                  f"à l'ID: {id}\n"
        return message , id

    def _get_maybe_existing_record(self, has_one) -> (str, int):
        """Return message and id for new or existing table record"""

        message = None
        id = 0
        if has_one["exist"] == "maybe":
            choices = self._show_existing_records(
                has_one["table"], has_one["show"])
            answer = input(has_one["question"])
            if answer==choices[-1]:
                message, id = self._new_table_record(has_one["entry"])
            else:
                id = choices[int(answer) - 1]
                message = f"Valeur de relation choisie: " \
                    f"{has_one['table']}, id: {id}\n"
        return message, id

    def _show_existing_records(self, table, field):
        """Print enumerated list of fields 'field' existing 'table' records
            and return a list of id and 'n': [id,.....,'n']"""

        choices = []
        sql = SQLShowRequest()
        sub_request = sql.table(table)
        request = re.sub(r'\*', f"id, {field}", sub_request)
        records = self._db.request(request, ask=True)
        for n, record in enumerate(records):
            choices.append(int(record[0]))
            string = "%3s) %s" % (n+1, record[1])
            print(string)
        choices.append("n")
        print("  n) -- Nouveau fournisseur --")
        return choices

    def _collect_many_relations(self, relations) -> str:
        """Add relations 'many-to-many' records and return message"""

        messages = ""
        for index, relation in enumerate(relations):
            self._relational_values.append({"through": relation["through"]})
            self._relational_values[index]["tables"] = []
            message, tables_values = self._collect_relation(
                relation, self._relational_values[index]["tables"])
            messages += message
        return messages

    def _collect_relation(self, relation, tables_values, rtv=False):
        """Collect relation and return message and values collected """

        i = 0
        messages = ""
        values = []
        while True:
            i += 1
            question = relation["question"] if i == 1 \
                else self._get_an_other(relation["question"])
            message, id_record = self._ask_relation(
                relation["entry"], question)
            if id_record:
                messages += message
                if rtv:
                    values.append(id_record)
                else:
                    if relation["entry"].has_many:
                        for other_relation in relation["entry"].has_many:
                            message, values = self._collect_relation(
                                other_relation, None, rtv=True)
                            if values:
                                messages += message
                                for value in values:
                                    tables_values.append({
                                        relation["table"]: id_record,
                                        other_relation["table"]: value})
                            else:
                                tables_values.append(
                                    {relation["table"]: id_record})
                    else:
                        tables_values.append(
                            {relation["table"]: id_record})
            else:
                break
        if rtv:
            return messages, values
        else:
            return messages, tables_values

    def _ask_relation(self, entry, question) -> (str, int):
        """Ask for add relation"""

        rec_id = None
        message = ""
        answer = input(question)
        if self.YES.match(answer):
            message, rec_id = self._new_table_record(entry)
        return message, rec_id

    def _record_has_many_links(self, target_id) -> str:
        """Record relations ids inside relational table of master
        record target"""

        messages = f"=== record relations for {str(self._entry)} at id " \
                   f"{target_id} ===\n"
        through =  self._sql.which_many_relations(
            str(self._entry), tables=False)
        messages += f"=== relational table is {through} ===\n"
        table_names = self._get_required_tables(through, fk=True)
        for relational_values in self._relational_values:
            request = self._sql.table(through , "script")
            many_values = self._get_many_values(
                target_id, relational_values["tables"], through)
            for values in many_values:
                success = self._db.request(request, values)
                if success:
                    messages += f"Record relation with FK: "\
                                f"{table_names} and "\
                                f"respective's id: {values}\n"
        return messages

    def _get_many_values(self, target_id, tables, through) -> list:
        """From entry dict and target_id, normalize and return
        data to record"""

        values = []
        entries_order = self._get_required_tables(through)
        for record_tables in tables:
            rec = [target_id]
            for required in entries_order:
                if required in record_tables:
                    rec.append(record_tables[required])
                elif required != str(self._entry):
                    rec.append(None)
            values.append(tuple(rec))
        return values

    def _get_required_tables(self, through, fk=False) -> list:
        """Return required tables from relational table name 'through'"""

        script = self._sql.table(through)["script"]
        entries_string = re.match(r'.*\((.*)\) VALUES.*', script)
        if fk:
            return  entries_string.group(1).split(", ")
        return re.sub('_id', '', entries_string.group(1)).split(", ")

    def _get_fields_values_for(self, fields) -> list:
        """Return values list for fields required"""

        values = list()
        for field in fields:
            if field["type"] == "varchar":
                value = None
                if field["test"] == "file":
                    is_file = False
                    while not is_file:
                        value = input(field["question"])
                        is_file = Path(value).is_file()
                        if not is_file:
                            print("Ce fichier n'existe pas... entrez un "
                                  "fichier qui existe svp")
                elif field["test"] == "image":
                    is_image =  False
                    while not is_image:
                        value = input(field["question"])
                        try:
                            img = Image.open(value)
                            img.close()
                        except IOError:
                            print("ce fichier n'est pas une image que "
                                  "je peux gérer "
                                  "(ou n'est pas une image)")
                            is_image = False
                        else:
                            is_image = True
                else:
                    value = input(field["question"])
                values.append(value)
            if field["type"] == "enum":
                correct_answer = None
                request = SQLShowRequest().type()
                enums = self._db.request(request,
                                         (field["type_name"],),
                                         ask=True)
                valid = re.compile(r"%s" % enums[0][2])
                while not correct_answer:
                    question = "{}({}) : ".format(field["question"],
                                                  enums[0][2])
                    answer = input(question)
                    correct_answer = valid.match(answer)
                values = [answer]
            if field["type"] == "bytea":
                value = input(field["question"]) \
                    if field["question"] else None
                if field["control"]:
                    if field["control"] == "password":
                        values.append(self._convert.password(value))
                    elif field["control"] == "thumb":
                        values.append(self._convert.thumb(values[-1])[1])
                    elif field["control"] == "salt":
                        values.append(self._convert.salt)
        return values

    @staticmethod
    def _get_an_other(string) -> str:
        """Add 'autre ' inside string at precise point"""

        point_to_insert = re.compile(r'^(.*ajouter un[e]? )(.*)$')
        match = point_to_insert.match(string)
        question = match.group(1) + "autre " + match.group(2)
        return question
