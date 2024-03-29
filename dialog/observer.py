"""Observer hold new record and print at the end"""


class Observer:
    """Observe"""

    def __init__(self):
        self._messages = "\n========= Résumé des actions ===========\n"
        self._debug = "\n======== DEBUG SQL =========\n"

    def add_record(self, table, id, values=None):
        """Tabel has been added"""

        if values:
            self._messages += f"Ajout d'un enregistrement sur {table}," \
                              f" à l'id {id} pour les valeurs: {values}\n"
        else:
            self._messages += f"Ajout d'un enregistrement sur {table}," \
                f" à l'id {id}\n"

    def add_relation_has_one(self, relation_table, id):
        """Add a new has_one relational table"""

        self._messages += f"Ajout de la relation unique {relation_table} " \
                         f"à l'id {id}\n"

    def add_relation_has_many(self, relation_table, id):
        """Add has_many relational record"""

        self._messages += f"Ajout de la relation {relation_table} " \
            f"à l'id {id}\n"

    def add_relation_link(self, through, values):
        """Add a has_many relational link record"""

        self._messages += f"Ajout d'un lien relationnel {through} " \
            f"avec les valeurs: {values}\n"

    def add_debug_message(self, text):
        """Add a debug message to be read or not"""

        self._debug += text + "\n"

    @property
    def messages(self):
        """Show what happened"""

        return self._messages

    @property
    def debug(self):
        """Debug property"""

        return self._debug