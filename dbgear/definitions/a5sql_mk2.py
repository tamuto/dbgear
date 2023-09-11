import csv
from dataclasses import dataclass
from dataclasses import field

from ..models.schema import Schema
from ..models.schema import Table
from ..models.schema import Field
from ..models.schema import Index


@dataclass
class Entity:
    instance: str = None
    table_name: str = None
    display_name: str = None
    fields: list = field(default_factory=list)
    indexes: list = field(default_factory=list)


@dataclass
class Relation:
    entity1: str = None
    entity2: str = None
    fields1: str = None
    fields2: str = None


class Parser:

    def __init__(self, mapping):
        self.mode = None
        self.mapping = mapping
        self.instances = {}
        self.relations = {}
        self.session = None

    def parse_line(self, line_no, line):
        if line == '':
            if self.mode == 2:
                if self.session.instance is not None:
                    if self.session.instance not in self.instances:
                        self.instances[self.session.instance] = []
                    self.instances[self.session.instance].append(self.session)
            if self.mode == 3:
                if self.session.entity2 not in self.relations:
                    self.relations[self.session.entity2] = {}
                for fld in self.session.fields2.split(','):
                    self.relations[self.session.entity2][fld] = self.session
            # 空行の場合、セッション解除
            self.mode = None
            return
        if line[0] == '#':
            return
        if self.mode is not None:
            name, value = self.split(line)
            if self.mode == 1:
                # 何もしない
                pass
            elif self.mode == 2:
                self.parse_entity(name, value)
            elif self.mode == 3:
                self.parse_relation(name, value)
            elif self.mode == 4:
                # コメントなので何もしない
                pass
            else:
                raise RuntimeError(f'Unknown Mode: {self.mode}')
        else:
            if line == '[Manager]':
                self.mode = 1
            elif line == '[Entity]':
                self.mode = 2
                self.session = Entity()
            elif line == '[Relation]':
                self.mode = 3
                self.session = Relation()
            elif line == '[Comment]':
                self.mode = 4
            else:
                raise RuntimeError(f'Unknown Line: ({line_no}) {line}')

    def split(self, line):
        work = line.split('=')
        if work[0] == "Index":
            # Indexは==となっている。
            # FIXME 恐らくIndex名を指定した場合を考慮する必要あり
            return work[0], work[2]
        return work[0], work[1]

    def parse_entity(self, name, value):
        if name == 'PName':
            self.session.table_name = value
        if name == 'LName':
            self.session.display_name = value
        if name == 'Page':
            value = value.upper()
            self.session.instance = self.mapping[value] if value in self.mapping else None
        if name == "Field":
            self.session.fields.append(value)
        if name == "Index":
            self.session.indexes.append(value)

    def parse_relation(self, name, value):
        if name == "Entity1":
            self.session.entity1 = value
        if name == "Entity2":
            self.session.entity2 = value
        if name == "Fields1":
            self.session.fields1 = value
        if name == "Fields2":
            self.session.fields2 = value


def convert_to_schema(p):
    schemas = {k: Schema(k) for k in p.instances.keys()}

    for key, entities in p.instances.items():
        for entity in entities:
            tbl = Table(
                instance=key,
                table_name=entity.table_name,
                display_name=entity.display_name
            )
            schemas[key].add_table(tbl)
            relation = p.relations[entity.table_name] if entity.table_name in p.relations else {}
            for row in csv.reader(entity.fields):
                # FIXME 恐らくdefault_valueの空文字初期化はうまく設定できない。
                field = Field(
                    display_name=row[0],
                    column_name=row[1],
                    column_type=row[2],
                    nullable=row[3] != 'NOT NULL',
                    primary_key=int(row[4]) if row[4] != '' else None,
                    default_value=row[5] if row[5] != '' else None,
                    foreign_key=relation[row[1]].entity1 if row[1] in relation else None,
                    comment=row[6] if row[6] != '' else None
                )
                tbl.fields.append(field)

            for row in csv.reader(entity.indexes):
                idx = Index(
                    index_name=None,
                    columns=row[1:]
                )
                tbl.indexes.append(idx)

    return schemas


def retrieve(folder, filename, mapping, **kwargs):
    p = Parser(mapping)
    with open(f'{folder}/{filename}', 'r', encoding='utf-8-sig') as f:
        for idx, line in enumerate(f):
            p.parse_line(idx + 1, line.strip())

    return convert_to_schema(p)
