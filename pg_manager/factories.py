"""Factories file for Record process depend to use case"""

from dialog import Creator, Observer


class Record:
    """Record Abstract Factory"""

    def __init__(self, target, **kwargs):
        record = None
        creator = Creator()
        self._observer = Observer()
        if target == "user":
            record = NewUser(self._observer)
        if target == "provider" or \
                target == "promotion" or \
                target == "code_accounting":
            record = NewHasOne(target, self._observer,
                               creator=creator._create_simple, **kwargs)
        if target == "nutriment" or \
                target == "drink" or \
                target == "option":
            record = NewHasOne(target, self._observer,
                               creator=creator._create_maybe, **kwargs)
        record.process()

    def show_messages(self):
        """Show observer_messages"""

        return self._observer.messages


class NewUser(Creator):
    """Process for record use case New user"""

    def __init__(self, observer):
        super().__init__("user")
        self._observer = observer

    def process(self):
        """New user Record process"""

        user_id = self._create_simple(self._entry)
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
        super().__init__(target)
        self._observer = observer
        self._creator = kwargs["creator"]
        self._file = kwargs["file"] if "file" in kwargs else None
        self._file_type = kwargs["file_type"] if "file_type" in kwargs \
            else None
        self._create_ = kwargs["creator"]

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
            request = self._sql.table(str(self._entry), "script")
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


