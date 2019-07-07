"""Filter for Field Postgresql Types values
(parser with actions on view)"""

from datetime import date, datetime
import re
from pathlib import Path
from PIL import Image

from tools import Convert
from models import SQLShowRequest
from pg_manager import  Database


class Field:
    """Act from field type (defined inside the XML file)"""

    IS_YES_OR_NO = re.compile(r'oui|non|o|n', re.IGNORECASE)
    IS_YES = re.compile(r'o|oui', re.IGNORECASE)
    IS_DATE = re.compile(r'^(0[1-9]|[1-2]\d|3[0-1])/(0[1-9]|1[0-2])/'
                         r'(20[1-3][0-9])$')
    IS_DATE_TIME = re.compile(r'^([0-1]\d|2[0-3]):([0-5][0-9]) (0[1-9]|'
                              r'[1-2]\d|3[0-1])/(0[1-9]|1[0-2])/'
                              r'(20[1-3][0-9])$')

    def __init__(self):
        self._convert = Convert()
        self._db = Database()

    def int_(self, field):
        """React for int field type"""

        value = input(field["question"])
        return int(value)

    def numeric_(self, field):
        """Numeric type field reaction"""

        value = input(field["question"])
        return float(value)

    def varchar_(self, field: dict) -> str:
        """React for varchar field type"""

        value = input(field["question"])
        return value

    def file_(self, field):
        """varchar type field with test = file"""

        value = None
        is_file = False
        while not is_file:
            value = input(field["question"])
            is_file = Path(value).is_file()
            if not is_file:
                print("Ce fichier n'existe pas... entrez un "
                      "fichier qui existe svp")
        return value

    def image_(self, field):
        """varchar type field with test = image"""

        value = None
        is_image = False
        while not is_image:
            value = input(field["question"])
            try:
                img = Image.open(value)
                img.close()
            except IOError:
                print("ce fichier n'est pas une image que "
                      "je peux pas gérer (ou n'est pas une image)")
                is_image = False
            else:
                is_image = True
        return value

    def enum_(self, field: dict) -> str:
        """React for enum field type"""

        correct_answer = None
        value = None
        request = SQLShowRequest().type()
        enums = self._db.request(request,
                                 (field["type_name"],),
                                 ask=True)
        valid = re.compile(r"%s" % enums[0][2])
        while not correct_answer:
            question = "{}({}) : ".format(field["question"],
                                          enums[0][2])
            value = input(question)
            correct_answer = valid.match(value)
        return value

    def bytea_(self, field: dict, values) -> bytes:
        """React for bytea field type"""

        value = input(field["question"]) if field["question"] else None
        if field["control"]:
            if field["control"] == "password":
                return self._convert.password(value)
            elif field["control"] == "thumb":
                return self._convert.thumb(values[-1])[1]
            elif field["control"] == "salt":
                return self._convert.salt

    def bool_(self, field: dict) -> bool:
        """React for bool field type"""

        value = None
        correct = None
        while not correct:
            value = input(field["question"])
            correct = self.IS_YES_OR_NO.match(value)
        return bool(self.IS_YES.match(value))

    def date_(self, field: dict) -> date:
        """React for date field type"""

        correct = False
        answer = None
        while not correct:
            question = field["question"] + " [DD/MM/YYY] "
            answer = input(question)
            correct = self.IS_DATE.match(answer)
        return datetime.strptime(answer, "%d/%m/%Y").date()

    def date_time_(self, field) -> datetime:
        """React for date_time field's type"""

        correct = False
        answer = None
        while not correct:
            question = field["question"] + "[HH:MM DD/MM/YYY] "
            answer = input(question)
            correct = self.IS_DATE_TIME.match(answer)
        return datetime.strptime(answer, "%H:%M %d/%m/%Y")

