"""Database connections control"""

import psycopg2

from config import PASSWORD


class Database():
    """Database can access Postgresql database oc-pizza"""

    connector = None

    def __init__(self):

        try:
            self.connector=psycopg2.connect(database="oc-pizza",
                                            user="oc-pizza",
                                            password=PASSWORD)
        except psycopg2.Error as e:
            print(e.pgerror)

    def __del__(self):

        if self.connector:
            self.connector.close()

    def request(self, request, values=None, ask=False) -> bool:
        """Send a request without any record, and return statement of
        transaction"""

        cursor = None
        test = ask
        records = list()
        try:
            cursor = self.connector.cursor()
            if values:
                cursor.execute(request, values)
            else:
                cursor.execute(request)
        except psycopg2.Error as e:
            print(e.pgerror)
            self.connector.rollback()
        else:
            try:
                self.connector.commit()
            except psycopg2.Error as e:
                print(e.pgerror)
                self.connector.rollback()
            else:
                if ask:
                    records = cursor.fetchall()
                else:
                    test = True
        finally:
            cursor.close()
        return records if ask else test



