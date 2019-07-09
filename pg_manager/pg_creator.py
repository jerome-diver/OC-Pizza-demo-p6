"""Create postgresql database if not exist and user/role"""

from subprocess import check_output, call

from . import Database
from models import SQLCreateRequest


class OCPizzaCreator():
    """Create database, tables, types, sequences, from xml file"""

    psql_call = ['psql', '-U', 'postgres', '-tc']

    def __init__(self):

        self._sql = SQLCreateRequest()
        self._success = ""
        self._warning = ""
        self._failed = ""

    @property
    def success(self):
        """Property for messages"""

        return self._success

    @property
    def warning(self):
        """Property for messages"""

        return self._warning

    @property
    def failed(self):
        """Property for messages"""

        return self._failed

    def all(self) -> bool:
        """Create all: user, database, types and tables"""

        self.user()
        self.database()
        self.types()
        self.tables()

    def user(self):
        """Create user/role for database oc-pizza if not exists"""

        cmd_user_exist = self.psql_call + [self._sql.user['test']]
        cmd_create_user = self._sql.command_list_for("user")
        user_exist = check_output(cmd_user_exist).decode().strip()
        if user_exist != '1':
            try:
                call(cmd_create_user)
            except Exception as err:
                self._failed += f"{err}\n"
        else:
            self._warning += "user exist already\n"

    def database(self):
        """Create database oc-pizza if not exists"""

        cmd_create_db = self._sql.command_list_for("database")
        cmd_exist_db = self.psql_call + [self._sql.database['test']]
        db_exist = check_output(cmd_exist_db).decode().strip()
        if db_exist != '1':
            try:
                call(cmd_create_db)
            except Exception as err:
                self._failed += f"{err}\n"
            else:
                self._success += "Database oc-pizza created"
        else:
            self._warning += "database oc-pizza exist already"

    def types(self):
        """Create 6 types to be used inside tables for
        oc-pizza database if not exists"""

        db = Database()
        types = self._sql.types
        for name, type_script in types.items():
            try:
                test = db.request(type_script)
            except Exception as err:
                self._failed += f"{err}\n"
            else:
                if not test:
                    self._failed += f"failed to create type: {name}\n"
                else:
                    self._success += f"success to create type: {name}\n"

    def tables(self):
        """Create 21 tables inside database oc-pizza if not exists"""

        db = Database()
        tables = self._sql.tables
        for name, table_script in tables.items():
            try:
                test = db.request(table_script)
            except Exception as err:
                self._failed += f"{err}\n"
            else:
                if not test:
                    self._failed += f"failed to create table: {name}\n"
                else:
                    self._success += f"success to create table: {name}\n"
