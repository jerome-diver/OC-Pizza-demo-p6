""" Import and parse from sql.xml file sql scripts"""

import xml.etree.ElementTree as ET
from pathlib import Path, PurePath


class SQL:
    """Import SQL data from sql_scripts.xml"""

    cwd = PurePath(Path('.').absolute())
    dir_xml = cwd / "xml"
    xml_file = str()
    scripts = None

    def __init__(self, xml_file_name):

        self.xml_file = self.dir_xml / xml_file_name
        self.scripts = ET.parse(str(self.xml_file))
        self._root = self.scripts.getroot()

    @property
    def root(self):
        """Property get root xml parsed file"""

        return self._root


class SQLCreateRequest(SQL):
    """Get create script from a xml file contain:
     <database>, <user>, <table name='my_table'>, <type name'my_type'>
     xml nodes"""

    def __init__(self):

        super().__init__("sql.xml")

    @property
    def database(self):
        """Property get database xml parsed file's data:
        create and test"""

        database = dict()
        for tag in self._root.find('database'):
            database[tag.tag] = tag.text
        return database

    @property
    def user(self):
        """Property get user xml parsed file's data:
        create and test"""

        user = dict()
        for tag in self._root.find('user'):
            user[tag.tag] = tag.text
        return user

    @property
    def types(self):
        """Property return type list creation scripts"""

        types = dict()
        for tag in self._root.find('types'):
            types[tag.attrib["name"]] = tag.text.strip()
        return types

    @property
    def tables(self):
        """Property return table list creation scripts"""

        tables = dict()
        for tag in self._root.find('tables'):
            tables[tag.attrib["name"]] = tag.text.strip()
        return tables

    def command_list_for(self, node):
        """Return list of element required for call process from
        subprocess.call"""

        elements = list()
        node_object = self._root.find(node)
        create = node_object.find("create")
        app = create.find("app")
        elements.append(app.text)
        options = create.find("options")
        for option in options.findall("option"):
            elements.append(option.attrib["type"])
            if option.text:
                elements.append(option.text)
        name = create.find("name")
        elements.append(name.text)
        comment = create.find("comment")
        elements.append(comment.text)
        return elements


class SQLInsertRequest(SQL):
    """Get insertion scripts from xml file with nodes:
    <insert name='my_table'>"""

    def __init__(self):

        super().__init__("sql_insert.xml")

    def table(self, table_name, extract=None):
        """Return dict of 'table_name' table insertion script,
        and fields list of field dictionary with:
        name, type, question items."""

        extract_able = (None, "table", "script", "fields", "relations",
                        "has_many", "has_one")
        script = ""
        fields = list()
        relations_dico = dict(has_many=[], has_one=[])
        for insert in self._root.findall("insert"):
            if insert.get('name') == table_name:
                script = " ".join(insert.find("script")\
                    .text.strip().replace("\n", "").split())
                for field in insert.findall("field"):
                    fields.append({
                        "name": field.get('name'),
                        "type": field.get("type"),
                        "type_name": field.get("t_name"),
                        "control": field.get("control"),
                        "test": field.get("test"),
                        "question": field.text
                    })
                for relations in insert.findall("relations"):
                    type = relations.get("type")
                    if type:
                        for relation in relations.findall("relation"):
                            dico = dict(
                                table=relation.get("table"),
                                question=relation.text,
                                exist=relation.get("exist"),
                                show=relation.get("show"))
                            if type == "has_many":
                                dico["through"] = relations.get("through")
                                dico["choose"] = relations.get("choose")
                            relations_dico[type].append(dico)
                break
        if extract not in extract_able:
            return None
        elif not extract:
            return {"table": table_name,
                    "script": script,
                    "fields": fields,
                    "relations": relations_dico}
        elif extract == "table":
            return table_name
        elif extract == "script":
            return script
        elif extract == "fields":
            return fields
        elif extract == "relations":
            return relations_dico
        elif extract == "has_many":
            return relations_dico["has_many"]
        elif extract == "has_one":
            return relations_dico["has_one"]

    def which_many_relations(self, target, tables=True):
        """Return list of tables related name if target has many relations"""

        tables_relations = []
        through = ""
        table = self._root.find(f".//insert[@name='{target}']")
        relations = table.find("relations[@type='has_many']")
        if relations:
            through = relations.get("through")
            if through:
                for relation in relations.findall("relation"):
                    tables_relations.append(relation.get("table"))
        if tables:
            return tables_relations
        return through


class SQLShowRequest(SQL):
    '''Show tables, records or any from "oc-pizza" database'''

    def __init__(self):
        super().__init__("sql_show.xml")

    def list(self):
        """Return tables list request"""

        db_node = self._root.find("database")
        tables_node = db_node.find("tables")
        list_node = tables_node.find("list")
        return list_node.text

    def columns(self):
        """Return table columns name, default value, type and
        is_nullabe request"""

        db_node = self._root.find("database")
        tables_node = db_node.find("tables")
        table_node = tables_node.find("table")
        return table_node.text

    def types(self):
        """Return SQL request for get types of 'oc-pizza' database"""

        db_node = self._root.find("database")
        types_node = db_node.find("types")
        return types_node.text

    def type(self):
        """Return request for show enum's values of target type"""

        db_node = self._root.find("database")
        type_node = db_node.find("type")
        return type_node.text

    def table(self, table):
        """return table request for show table content records"""

        tables = self._root.find("tables")
        table_ = tables.find(f"table[@name='{table}']")
        request = table_.text
        return request
