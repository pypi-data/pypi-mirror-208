from typing import List

from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.ext.automap import automap_base

from pkg.tool.convert import to_upper_camel_case, dict2params_str


def table_model_gen(url, schemas=None, table_names=None, file=None, add=False, ignore=True):
    packages = {
        "sqlalchemy.ext.declarative": ["declarative_base"],
        "sqlalchemy": ["Column"]
    }
    engine = create_engine(url, pool_recycle=7200)
    isp = inspect(engine)
    if engine.url.database is not None:
        dbs = [engine.url.database]
    elif schemas is not None:
        dbs = schemas
    else:
        dbs = isp.get_schema_names()
    db_table_info_map = dict()
    for db in dbs:
        if table_names is None:
            db_tables = isp.get_table_names(schema=db)
        else:
            db_tables = table_names
        if db not in db_table_info_map:
            db_table_info_map[db] = dict()
        for t in db_tables:
            if t not in db_table_info_map[db]:
                db_table_info_map[db][t] = dict()
            if "columns" not in db_table_info_map[db][t]:
                db_table_info_map[db][t]["columns"] = []

    for db in dbs:
        metadata = MetaData()
        metadata.reflect(bind=engine, schema=db)
        db_tables = list(db_table_info_map.get(db, {}).keys())
        for t in metadata.tables.values():
            if t.name in db_tables:
                if t.schema not in db_table_info_map:
                    db_table_info_map[t.schema] = dict()
                if t.name not in db_table_info_map[t.schema]:
                    db_table_info_map[t.schema][t.name] = dict()
                if "table_args" not in db_table_info_map[t.schema][t.name]:
                    db_table_info_map[t.schema][t.name]["table_args"] = {
                        "comment": t.comment
                    }
                    if add:
                        db_table_info_map[t.schema][t.name]["table_args"]["schema"] = t.schema
                    # if t.indexes:
                    #     db_table_info_map[t.schema][t.name]["table_args"]["indexes"] = set()
                    #     for index in t.indexes:
                    #         expressions = []
                    #         if hasattr(index, 'expressions'):
                    #             for e in index.expressions:
                    #                 if isinstance(e, Column):
                    #                     expressions.append(
                    #                         Column(Table(t.name, MetaData()), name=e.name, type_=e.type))
                    #                     field_module = e.type.__class__.__module__
                    #                     field_class_name = e.type.__class__.__name__
                    #                     if field_module not in packages:
                    #                         packages[field_module] = []
                    #                     packages[field_module].append(field_class_name)
                    #         db_table_info_map[t.schema][t.name]["table_args"]["indexes"].add(
                    #             Index(index.name, *expressions))

                if t.primary_key:
                    if "primary_key" not in db_table_info_map[t.schema][t.name]:
                        db_table_info_map[t.schema][t.name]["primary_key"] = []
                    primary_key = t.primary_key
                    if primary_key:
                        for pk in primary_key:
                            db_table_info_map[t.schema][t.name]["primary_key"].append(pk.name)
                if t.foreign_keys:
                    if "foreign_key" not in db_table_info_map[t.schema][t.name]:
                        db_table_info_map[t.schema][t.name]["foreign_key"] = dict()
                    for foreign_key in t.foreign_keys:
                        if hasattr(foreign_key, "column"):
                            parent_db = foreign_key.column.table.schema
                            parent_table = foreign_key.column.table.name
                            parent_field = foreign_key.column.name
                            child_db = t.schema
                            child_table = t.name
                            child_field = foreign_key.name
                            if parent_db not in db_table_info_map:
                                db_table_info_map[parent_db] = dict()
                            if parent_table not in db_table_info_map[parent_db]:
                                db_table_info_map[parent_db][parent_table] = dict()
                            if "relationship" not in db_table_info_map[parent_db][parent_table]:
                                db_table_info_map[parent_db][parent_table]["relationship"] = dict()
                            if child_table not in db_table_info_map[parent_db][parent_table]["relationship"]:
                                db_table_info_map[parent_db][parent_table]["relationship"][child_table] = dict()
                            db_table_info_map[parent_db][parent_table]["relationship"][child_table].update({
                                "parent_db": parent_db,
                                "parent_table": parent_table,
                                "parent_field": parent_field,
                                "child_db": child_db,
                                "child_table": child_table,
                                "child_field": child_field})
                            if child_table not in db_table_info_map[t.schema]:
                                db_table_info_map[t.schema][child_table] = dict()
                            if "foreign_key" not in db_table_info_map[t.schema][child_table]:
                                db_table_info_map[t.schema][child_table]["foreign_key"] = dict()
                            if child_field not in db_table_info_map[t.schema][child_table]:
                                foreign_key_column = fr'{parent_table}.{parent_field}' if not add else \
                                    fr'{parent_db}.{parent_table}.{parent_field}'
                                foreign_key_params = {
                                    "column": foreign_key_column
                                }
                                if foreign_key.use_alter is not None:
                                    foreign_key_params.update({
                                        "use_alter": foreign_key.use_alter
                                    })
                                if foreign_key.onupdate is not None:
                                    foreign_key_params.update({
                                        "onupdate": foreign_key.onupdate
                                    })
                                if foreign_key.ondelete is not None:
                                    foreign_key_params.update({
                                        "ondelete": foreign_key.ondelete
                                    })
                                if foreign_key.link_to_name is not None:
                                    foreign_key_params.update({
                                        "link_to_name": foreign_key.link_to_name
                                    })
                                foreign_key_str = ', '.join([f"{k}={repr(v) if isinstance(v, str) else v}" for k, v in
                                                             foreign_key_params.items()])
                                db_table_info_map[t.schema][child_table]["foreign_key"][
                                    child_field] = f"ForeignKey({foreign_key_str})"

    for db, db_indo in db_table_info_map.items():
        for table, table_info in db_indo.items():
            table_info["columns"]: List[dict] = isp.get_columns(table, schema=db)
            table_name = f"{db}_{table}" if add else table
            class_class_name_str = f"""\n\nclass {to_upper_camel_case(table_name)}(Base):"""
            table_args = table_info.get("table_args", {})
            table_args_str = ""
            if table_args:
                table_args_str = "\n    __table_args__ = %r" % table_args
                packages["sqlalchemy.sql.schema"] = ["Index"]
            table_name_str = f"\n    __tablename__ = '{table}'"
            table_class_str = f"""{class_class_name_str}{table_name_str}{table_args_str}\n\n"""
            metadata = MetaData()
            metadata.reflect(bind=engine, schema=db)
            base = automap_base(metadata=metadata)
            base.prepare()
            relationship = db_table_info_map.get(db, {}).get(table, {}).get("relationship", {})
            if relationship:
                for child_table, relationship_info in relationship.items():
                    child_db = relationship_info.get("child_db")
                    parent_db = relationship_info.get("parent_db")
                    parent_table = relationship_info.get("parent_table")
                    relation_table = f"{child_db}_{child_table}" if add else child_table
                    self_table = f"{parent_db}_{parent_table}" if add else parent_table
                    table_info["columns"].append(
                        {f'{relation_table}': f"relationship('{to_upper_camel_case(relation_table)}',"
                                              f" backref='{self_table}')",
                         "name": f'{relation_table}', "is_relation_field": True})

            for column in table_info["columns"]:
                if 'foreign_key' in db_table_info_map[db][table]:
                    for k, v in db_table_info_map[db][table]['foreign_key'].items():
                        if isinstance(column, dict):
                            if k == column.get("name"):
                                if "foreign_keys" not in column:
                                    column["foreign_keys"] = []
                                column["foreign_keys"].append(v)
                                packages["sqlalchemy"].append("ForeignKey")

                if column.get("name") in db_table_info_map.get(db).get(table).get("primary_key", []):
                    column["primary_key"] = True
                field_type = column.get("type")
                if field_type:
                    field_module = field_type.__class__.__module__
                    field_class_name = field_type.__class__.__name__
                    if field_module not in packages:
                        packages[field_module] = []
                    if field_class_name not in packages[field_module]:
                        packages[field_module].append(field_class_name)
                if "type" in column:
                    column["type_"] = column.pop("type")
                if "default" in column:
                    column["server_default"] = column.pop("default")
                if not column.get("is_relation_field"):
                    table_class_str += f"    {column.get('name')} = Column({dict2params_str(column)})\n"
                else:
                    relationship = column.get(column.get('name'))
                    table_class_str += f"    {column.get('name')} = {relationship}"
                    packages["sqlalchemy.orm"] = ["relationship"]
            table_info["class_model"] = table_class_str

    file_content = "# coding: utf-8\n\n"
    for p, c in packages.items():
        file_content += f'from {p} import {", ".join(c)}\n'
    file_content += "\nBase = declarative_base()\n"

    for db, db_indo in db_table_info_map.items():
        for table, table_info in db_indo.items():
            file_content += table_info.get("class_model")
    if file:
        with open(file, "w+") as f:
            f.write(file_content)
    else:
        print(file_content)
