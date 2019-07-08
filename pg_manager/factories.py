"""Factories file for Record process depend to use case"""

import re

from models import SQLInsertRequest, SQLShowRequest, TableEntry, Field
from pg_manager import Database
from tools import Convert
from dialog import Observer


class Creator:
    """Create records"""

    YES = re.compile(r'o|y|oui|yes', re.IGNORECASE)
    ADD_A = re.compile(r'^(.*ajouter un[e]? )(.*)$', re.IGNORECASE)
    CHOOSE = re.compile(r'.*\[(.*)\].*', re.IGNORECASE)

    def __init__(self, target=None, observer=None):

        self._sql = SQLInsertRequest()
        self._db = Database()
        self._convert = Convert()
        if target:
            self._entry = TableEntry(target)
        if observer:
            self._observer = observer
        self._field = Field()

    @property
    def entry(self):
        """Property entry"""

        return self._entry

    def _create_simple(self, arg):
        """ask for fields entry and record, then return id"""

        id = []
        entry = arg if isinstance(arg, TableEntry) else arg["entry"]
        while not id:
            values = self._get_fields_values_for(entry.fields)
            request = entry.request
            if self._observer:
                self._observer.add_debug_message(
                    f"request: {request}\n ==> values: {values}")
            id = self._db.request(request, tuple(values), ask=True)
        return int(id[0][0])

    def _create_maybe(self, relation, **kwargs):
        """ask from a list of records to choose one (exist=yes)
        or (exist=maybe) possibly create a new one
        or STOP link recording"""

        id = 0
        while id == 0:
            if relation["exist"]:
                choices = self._show_existing_records(
                    relation["table"],
                    relation["show"],
                    relation["exist"],
                    **kwargs)
                answer = input("Faites un choix: ")
                if relation["exist"] == "maybe" and answer==choices[-1]:
                    Record(relation["table"])
                elif 1 <= int(answer) < len(choices):
                    id = choices[int(answer)]
                elif int(answer) >= len(choices):
                    print("re-essayez: vous avez fait un choix qui n'existe "
                          "pas.")
                else:   # Choice is 0 ==> STOP
                    id = None
        return id

    def _record_through(self, through, values):
        """Record relational table"""

        request = self._sql.table(through, "script")
        if self._observer:
            self._observer.add_debug_message(
                f"request: {request}\n ==> values: {values}")
        success = self._db.request(request, tuple(values))
        return success

    def _get_fields_values_for(self, fields, exception=[]) -> list:
        """Return field parser factories result list values"""

        values = list()
        for field in fields:
            if field["name"] not in exception:
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
                if field["type"] == "date_time":
                    value = self._field.date_time_(field)
                if field["type"] == "numeric":
                    value = self._field.numeric_(field)
                values.append(value)
        return values

    @staticmethod
    def _get_an_other(string) -> str:
        """Add 'autre ' inside string at precise point"""

        match = Creator.ADD_A.match(string)
        question = match.group(1) + "autre " + match.group(2)
        return question

    def _show_existing_records(self, table, fields, exist, **kwargs):
        """Print enumerated list of fields 'field' existing 'table' records
            and return a list of id and 'n': [id,.....,'n']"""

        choices = ["STOP"]
        print("  0) -- RIEN --")
        sql = SQLShowRequest()
        sub_request = sql.table(table)
        request = re.sub(r'\*', f"id, {fields}", sub_request) \
            if "request" not in kwargs or kwargs["request"] is None\
            else kwargs["request"]
        records = self._db.request(request, ask=True)\
            if "values" not in kwargs \
            else self._db.request(request, kwargs["values"], ask=True)
        if self._observer:
            self._observer.add_debug_message(
                f"request: {request}\n ==> answer: {records}")
        for n, record in enumerate(records):
            choices.append(int(record[0]))
            string = "%3s) " % str(n+1)
            for i_field in range(1, len(record)):
                string += f" %s - " % record[i_field]
            print(string)
        if exist == "maybe":
            choices.append("n")
            print("  n) -- Nouveau --")
        return choices

    def ask_for_choice(self, question):
        """Ask a question and return the answer depend of the validation of
        choices"""

        correct = False
        answer = ""
        choices = self.CHOOSE.match(question).group(1).split(", ")
        while not correct:
            answer = input(question)
            correct = bool((answer in choices) or "fin")
        return answer


class Record:
    """Record Abstract Factory"""

    OBSERVER = Observer()
    CREATOR = Creator(observer=OBSERVER)

    def __init__(self, target, **kwargs):
        record = None
        if target == "user":
            record = NewUser(self.OBSERVER)
        if target == "provider" or \
                target == "promotion" or \
                target == "code_accounting":
            create_simple = getattr(self.CREATOR, "_create_simple")
            record = NewHasOne(target, self.OBSERVER,
                               creator=create_simple, **kwargs)
        if target == "nutriment" or \
                target == "drink" or \
                target == "option":
            create_maybe = getattr(self.CREATOR, "_create_maybe")
            record = NewHasOne(target, self.OBSERVER,
                               creator=create_maybe, **kwargs)
        if target == "pizza":
            record = NewPizza(self.OBSERVER)
        if target == "restaurant":
            record = NewRestaurant(self.OBSERVER)
        if target == "stock":
            record = NewStock(self.OBSERVER)
        if target == "order":
            record = NewOrder(self.OBSERVER)
        record.process()

    def show_messages(self):
        """Show observer_messages"""

        return self.OBSERVER.messages

    def show_debug(self):
        """Show debug observer messages"""

        return self.OBSERVER.debug


class NewUser(Creator):
    """Process for record use case New user"""

    def __init__(self, observer):
        super().__init__("user", observer=observer)
        self._observer = observer

    def process(self):
        """New user Record process"""

        user_id = self._create_simple(self.entry)
        self._observer.add_record("user", user_id)
        for relation in self.entry.has_many:
            through = relation["through"]
            values = [user_id]
            self._record_user_relations(through, relation, values)

    def _record_user_relations(self, through, relation, values_):
        """Record only user's relations recursively"""

        add_relation = True
        i_relation = 0
        while add_relation:
            i_relation += 1
            values = values_
            question = relation["question"] if i_relation == 1 \
                else self._get_an_other(relation["question"])
            add_relation = self.YES.match(input(question))
            if add_relation:
                id_record = self._create_simple(relation)
                self._observer.add_relation_has_many(
                    relation["table"], id_record)
                if relation["table"] == "address":
                    values.append(id_record)
                    self._record_user_relations(
                            through, relation["entry"].has_many[0],
                            values)
                    continue
                elif len(values) == 1:
                    values += [None, id_record]
                elif len(values) == 2:
                    values.append(id_record)
                self._record_relation_through(through, values)

    def _record_relation_through(self, through, values):
        """Record through linker relational table"""

        ok = self._record_through(through, values)
        if ok:
            self._observer.add_relation_link(through, values)


class NewHasOne(Creator):
    """Process for new record (not maybe creator):
    provider | promotion | code_accounting record
    (maybe creator):
    nutriment | drink | option"""

    def __init__(self, target, observer, **kwargs):
        super().__init__(target, observer=observer)
        self._observer = observer
        self._creator = kwargs["creator"]
        self._file = kwargs["file"] if "file" in kwargs else None
        self._file_type = kwargs["file_type"] \
            if "file_type" in kwargs \
            else None

    def process(self):
        """Process to record any new
        provider|promotion|code_accounting (exist = None)
        nutriment|drink|option (exist = maybe|yes)"""

        if self._file_type:
            self._record_from_file()
        else:
            values = self._get_fields_values_for(self.entry.fields)
            for relation in self.entry.has_one:
                add_relation = True
                if relation["exist"] is None:
                    add_relation = self.YES.match(input(relation["question"]))
                else:
                    print(relation["question"])
                if add_relation:
                    id_record = self._creator(relation)
                    values.append(id_record)
                    self._observer.add_relation_has_one(
                        relation["table"], id_record)
                else:
                    values.append(None)
            request = self._entry.request
            id = self._db.request(request, tuple(values), ask=True)
            self._observer.add_record(str(self.entry),
                                      int(id[0][0]),
                                      values)

    def _record_from_file(self):
        """Record data from file content list of entries"""

        if self._file_type == "csv":
            char_separator = input("Quelle est le caractère de "
                                   "séparation du fichier CSV svp ? ")
            PCG = []
            with open(self._file, 'r') as pcg:
                for line in pcg:
                    PCG.append(tuple(line.strip().split(char_separator)))
            request = self._sql.table(str(self._entry), "script")
            for pcg_values in PCG:
                id = self._db.request(request, pcg_values, ask=True)
                self._observer.add_record(str(self._entry), id)


class NewPizza(Creator):
    """Record a new pizza"""

    def __init__(self, observer):
        super().__init__("pizza", observer=observer)
        self._observer = observer

    def process(self):
        """Process new record for pizza"""

        pizza_id = self._create_simple(self.entry)
        self._observer.add_record("pizza", pizza_id)
        for relation in self.entry.has_many:
            nutriment_id = True
            while nutriment_id is not None:
                nutriment_id = self._create_maybe(relation)
                through = relation["through"]
                nutriment_entry = TableEntry(through)
                if isinstance(nutriment_id, int):
                    success = False
                    while not success:
                        values = self._get_fields_values_for(
                            nutriment_entry.fields)
                        recipe_values = values + [pizza_id, nutriment_id]
                        request = nutriment_entry.request
                        success = self._db.request(request,
                                                   tuple(recipe_values))
                        if success:
                            self._observer.add_relation_link(
                                through, recipe_values)
                        else:
                            self._observer.add_debug_message(
                                f"Failed to record link relations {through}")


class NewRestaurant(Creator):
    """New record restaurant factory"""

    def __init__(self, observer):
        super().__init__("restaurant", observer=observer)
        self._observer = observer

    def process(self):
        """Process for record new restaurant"""

        values = self._get_fields_values_for(self._entry.fields)
        for relation in self.entry.has_one:
            print(relation["question"])
            values.append(self._create_simple(relation))
            self._observer.add_relation_has_one(
                relation["table"], values[-1])
        request = self._entry.request
        restaurant_id = self._db.request(
            request, tuple(values), ask=True)[0][0]
        self._observer.add_record("restaurant", restaurant_id)
        # Find and record has_many relation through menu_price:
        relation_id = 0
        while relation_id is not None:
            values = [restaurant_id]
            relations = self._entry.has_many
            choose_question = relations[0]["choose"]
            through = relations[0]["through"]
            answer = self.ask_for_choice(choose_question)
            if answer == "fin":
                relation_id = None
            else:
                if answer == "boisson":
                    answer = "drink"
                cl = ["drink" if x == "boisson" else x for x in cl]
                menus_price_entry = TableEntry(through)
                fields_values = [None] if answer != "pizza" else []
                exception = ["size_pizza"] if answer != "pizza" else []
                for relation in relations:
                    if relation["table"] == answer:
                        relation_id = self._create_maybe(relation)
                        if relation_id:
                            self._observer.add_relation_has_many(
                                relation["table"], relation_id)
                            fields_values += self._get_fields_values_for(
                                    menus_price_entry.fields, exception)
                            values += [relation_id
                                       if x == answer
                                       else None
                                       for x in cl]
                            values += fields_values
                            success = self._record_through(
                                through, values)
                            if success:
                                self._observer.add_relation_link(
                                    through, values)


class NewStock(Creator):
    """New stock record factory"""

    def __init__(self, observer):
        super().__init__("stock", observer=observer)
        self._observer = observer

    def process(self):
        """Process new stock record"""

        print("Nouveau ajout de stock\n")
        restaurant_relation = self._entry.find_relation("restaurant")
        print(restaurant_relation["question"])
        restaurant_id = self._create_maybe(restaurant_relation)
        request = self._entry.request
        relation_id = 0
        while relation_id is not None:
            values = [restaurant_id]
            cq = self._entry.has_one[0]["choose"]
            answer = self.ask_for_choice(cq)
            if answer == "fin":
                relation_id = None
            else:
                cl = ["nutriment", "drink"]
                answer = "drink" if answer == "boisson" else "nutriment"
                for relation in self._entry.has_one:
                    if relation["table"] == answer:
                        relation_id = self._create_maybe(relation)
                        if relation_id:
                            self._observer.add_relation_has_one(
                                relation["table"], relation_id)
                            values += [relation_id if x == answer
                                       else None
                                       for x in cl]
                            values += self._get_fields_values_for(
                                self._entry.fields)
                            stock_id = self._db.request(
                                request, tuple(values), ask=True)[0][0]
                            self._observer.add_record(
                                self.entry, stock_id, values)


class NewOrder(Creator):
    """Record a new order factory"""

    def __init__(self, observer):
        super().__init__("order", observer=observer)
        self._observer = observer

    def process(self):
        """Process for record a new order"""

        print("Nouvelle commande\n(doit concerner un restaurant et un "
              "utilisateur enregistré)")
        request = self._entry.request
        values = []
        restaurant_id = 0
        through = self._sql.which_many_relations("order", False)
        user_id = 0
        for relation in self._entry.has_one:
            print(relation["question"])
            if relation["table"] != "address":
                relation_id = self._create_maybe(relation)
            if relation["table"] == "restaurant":
                restaurant_id = relation_id
            if relation["table"] == "user":
                user_id = relation_id
            if relation["table"] == "address":
                relation_id = self._create_maybe(
                    relation,
                    request=relation["request"],
                    values=(user_id,))
            values.append(relation_id)
        values += self._get_fields_values_for(self._entry.fields)
        order_id = self._db.request(request, values, ask=True)[0][0]
        self._observer.add_record(self._entry, order_id, values)
        relation_id = 0
        while relation_id is not None:
            values = [order_id]
            cq = self._entry.has_many[0]["choose"]
            answer = self.ask_for_choice(cq)
            if answer == "fin":
                relation_id = None
            else:
                cl = ["pizza", "drink"]
                answer = "drink" if answer == "boisson" else "pizza"
                for relation in self._entry.has_many:
                    if relation["table"] != "prommotion":
                        request = relation["request"]
                    if relation["table"] == answer:
                        relation_id = self._create_maybe(
                            relation, request=request,
                            values=(restaurant_id,))
                        if relation_id:
                            self._observer.add_relation_has_one(
                                relation["table"], relation_id)
                            values += [relation_id if x == answer
                                       else None
                                       for x in cl]
                    if relation["table"] == "option" and answer == "pizza":
                        cq = "Voulez-vous ajouter une option ? "\
                             " [oui/non] "
                        answer = self.ask_for_choice(cq)
                        if self.YES.match(answer):
                            option_id = self._create_maybe(
                                relation, request=request,
                                values=(restaurant_id,))
                            self._observer.add_relation_has_many(
                                "option", option_id)
                            values.append(option_id)
                        else:
                            values.append(None)
                    elif relation["table"] == "option" and answer != "pizza":
                        values.append(None)
                    if relation["table"] == "promotion":
                        print(relation["question"])
                        promotion_id = self._create_maybe(relation)
                        self._observer.add_relation_has_many(
                            "promotion", promotion_id)
                        values.append(promotion_id)
                link_entry = TableEntry(through)
                if values[1] is not None:
                    values += self._get_fields_values_for(
                        link_entry.fields)
                else:
                    values.append(None) # Non size for drink order detail
                    values += self._get_fields_values_for(
                        link_entry.fields, "size")
                ok = self._record_through(through, values)
                if ok:
                    self._observer.add_relation_link(through, values)


