"""Create postgresql database if not exist and user/role"""

from subprocess import check_output, call

from . import Database
from models import SQLCreateRequest


class OCPizzaCreator():
    """Create database, tables, types, sequences, from xml file"""

    psql_call = ['psql', '-U', 'postgres', '-tc']

    def __init__(self):

        self._sql = SQLCreateRequest()

    def all(self) -> bool:
        """Create all: user, database, types and tables"""

        if self.user():
            if self.database():
                if self.types():
                    return self.tables()
        return False

    def user(self) -> bool:
        """Create user/role for database oc-pizza if not exists"""

        cmd_user_exist = self.psql_call + [self._sql.user['test']]
        cmd_create_user = self._sql.command_list_for("user")
        user_exist = check_output(cmd_user_exist).decode().strip()
        if user_exist != '1':
            try:
                call(cmd_create_user)
            except Exception as err:
                print(err)
                return False
            else:
                return True
        else:
            print("user exist already")
            return False

    def database(self) -> bool:
        """Create database oc-pizza if not exists"""

        cmd_create_db = self._sql.command_list_for("database")
        cmd_exist_db = self.psql_call + [self._sql.database['test']]
        db_exist = check_output(cmd_exist_db).decode().strip()
        if db_exist != '1':
            try:
                call(cmd_create_db)
            except Exception as err:
                print(err)
                return False
            else:
                return True
        else:
            print("db exist already")
            return False

    def types(self) -> bool:
        """Create 6 types to be used inside tables for
        oc-pizza database if not exists"""

        db = Database()
        types = self._sql.types
        for name, type_script in types.items():
            try:
                test = db.request(type_script)
            except Exception as error:
                print("no one type can be create")
                return False
            else:
                if not test:
                    print("failed to create type:", name)
                else:
                    print("success to create type:", name)
        return True

    def tables(self) -> bool:
        """Create 21 tables inside database oc-pizza if not exists"""

        db = Database()
        tables = self._sql.tables
        for name, table_script in tables.items():
            try:
                test = db.request(table_script)
            except Exception as error:
                print("no one table can be create")
                return False
            else:
                if not test:
                    print("failed to create table:", name)
                else:
                    print("success to create table:", name)
        return True
