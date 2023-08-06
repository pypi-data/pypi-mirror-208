"""sqlite3 连接操作类"""
import sqlite3
from pathlib import Path
from enum import Enum
from contextlib import contextmanager
from multiprocessing import Lock
from typing import Iterator, List, Any, Type, Union
from vxutils.dataclass import (
    vxBoolField,
    vxDataClass,
    vxField,
    vxFloatField,
    vxIntField,
    vxUUIDField,
    vxDatetimeField,
    vxPropertyField,
    vxBytesField,
    vxDict,
)
from vxutils.database.base import vxDataBase
from vxutils import logger

column_type_map = {
    vxFloatField: "DOUBLE",
    vxIntField: "INT",
    vxDatetimeField: "DATETIME",
    vxBoolField: "BOOLEAN",
    vxUUIDField: "TEXT",
    vxPropertyField: "NUMERIC",
    vxBytesField: "GLOB",
}

SHARED_MEMORY_DATABASE = "file:vxquantdb?mode=memory&cache=shared"


def dict_factory(cursor, row):
    """sqlite3.row_factory的子类，用于将查询结果转换为vxDict对象"""
    fields = [column[0] for column in cursor.description]
    return vxDict(zip(fields, row))


class vxSQLiteDB(sqlite3.Connection, vxDataBase):
    """sqlite3.Connection的子类，用于增加对vxDataClass对象ORM支持"""

    __dbconnections__ = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.row_factory = dict_factory
        self._tblmapping = {}
        self._lock = Lock()

    @classmethod
    def connect(cls, db_uri: str = SHARED_MEMORY_DATABASE, **kwargs) -> "vxSQLiteDB":
        """连接sqlite3数据库

        Keyword Arguments:
            db_uri {str} -- 连接uri (default: {SHARED_MEMORY_DATABASE})
            timeout {float} -- 超时时间，默认5s (default: {5})

        Returns:
            vxSQLiteDB -- 返回已创建连接
        """
        timeout = kwargs.get("timeout", 5)
        key = (
            db_uri if db_uri == SHARED_MEMORY_DATABASE else str(Path(db_uri).absolute())
        )
        if key not in cls.__dbconnections__:
            dbconn = sqlite3.connect(
                db_uri,
                timeout,
                factory=cls,
                uri=True,
                check_same_thread=False,
                **kwargs,
            )
            cls.__dbconnections__[key] = dbconn
        return cls.__dbconnections__[key]

    def disconnect(self) -> None:
        self.close()

    def create_table(
        self,
        table_name: str,
        primary_keys: List[str],
        vxdatacls: Type[vxDataClass],
        if_exists: str = "SKIP",
    ) -> "vxDataBase":
        """创建数据表格和vxdataclass的映射关系

        Arguments:
            table_name {str} -- 数据表名称
            primary_keys {List[str]} -- 数据表主键
            vxdatacls {Type[vxDataClass]} -- vxdataclass类型

        Keyword Arguments:
            if_exists {str} -- 若存在时，SKIP，跳过 | DELETE ，先删除表格，后创建 (default: {"SKIP"})

        Returns:
            None -- 无返回值
        """
        column_def = []

        for name, vxfield in vxdatacls.__dict__.items():
            if not isinstance(vxfield, vxField):
                continue
            column_type = column_type_map.get(vxfield.__class__, "TEXT")
            if name in primary_keys:
                column_type = f"{column_type} NOT NULL"

            column_def.append(f"'{name}' {column_type}")

        if primary_keys:
            primary_key_string = f"""PRIMARY KEY(`{"`,`".join(primary_keys)}`)"""
            sql = f"""CREATE TABLE IF NOT EXISTS `{table_name}` 
                    ({','.join(column_def)},{primary_key_string});"""
        else:
            sql = f"""CREATE TABLE IF NOT EXISTS `{self._table_name}` 
                    ({','.join(column_def)});"""

        with self:
            if if_exists.upper() == "DELETE":
                self.execute(f"""DROP TABLE IF EXISTS {table_name};""")
            self.execute(sql)
        self._tblmapping[table_name] = (primary_keys, vxdatacls)

    def drop_table(self, table_name: str):
        """删除数据表格以及映射关系

        Arguments:
            table_name {str} -- 数据表格名称

        Returns:
            若表格不存在，直接返回
        """
        if table_name not in self._tblmapping:
            logger.warning(f"Table {table_name} not exists")
            return

        with self:
            self.execute(f"""DROP TABLE IF EXISTS `{table_name}`;""")

    def distinct(self, table_name: str, col: str, *conditions, **query) -> List:
        """获取数据表格中指定列的不重复值

        Arguments:
            table_name {str} -- 数据表格名称
            col {str} -- 列名称

        Returns:
            List -- col不重复的字段列表
        """
        sql = f"""SELECT DISTINCT `{col}` FROM `{table_name}`"""
        query_conditions = list(conditions)

        if query:
            query_conditions.extend(
                [f"{key}='{value or ''}'" for key, value in query.items()]
            )
        if query_conditions:
            sql += f""" WHERE {' and '.join(query_conditions)}"""
        sql += ";"

        return [item[col] for item in self.execute(sql)]

    def save(self, table_name: str, *vxdataobjs: Any) -> "vxSQLiteDB":
        """保存数据对象到数据库

        Arguments:
            table_name {str} -- 数据表格名称

        Returns:
            vxSQLiteDB -- 返回自身
        """
        if len(vxdataobjs) == 1 and isinstance(vxdataobjs[0], (list, tuple)):
            vxdataobjs = vxdataobjs[0]

        _, vxdatacls = self._tblmapping[table_name]
        fields = list(vxdatacls.__vxfields__.keys())
        sql = f"""INSERT OR REPLACE INTO `{table_name}` 
                ({','.join(fields)}) \n\tVALUES ({','.join(['?'] * len(fields))})"""
        datas = []
        for obj in vxdataobjs:
            if not isinstance(obj, vxDataClass):
                logger.error(
                    f"obj 类型{obj.__class__.__name__}不为{vxdatacls.__name__}，跳过:"
                    f" {obj}"
                )
                continue

            values = []
            for col in fields:
                value = getattr(obj, col)
                if value is None:
                    value = ""
                elif value is False:
                    value = 0
                elif value is True:
                    value = 1
                elif isinstance(value, Enum):
                    value = value.name

                values.append(value)
            datas.append(values)

        with self:
            self.executemany(sql, datas)
        return self

    def find(self, table_name: str, *conditions, **query) -> Iterator:
        """查找数据表格中的数据，并返回vxdataclass对象

        Arguments:
            table_name {str} -- 数据表格名称

        Yields:
            Iterator -- 返回vxdataclass对象
        """
        sql = f"""SELECT * FROM `{table_name}`"""
        query_conditions = list(conditions)
        _, vxdatacls = self._tblmapping[table_name]
        if query:
            query_conditions.extend(
                [f"{key}='{value or ''}'" for key, value in query.items()]
            )
        if query_conditions:
            sql += f""" WHERE {' and '.join(query_conditions)}"""
        sql += ";"

        for row in self.execute(sql):
            yield vxdatacls(**row)

    def findone(self, table_name: str, *conditions, **query) -> vxDataClass:
        """查找一个数据表格中的数据，并返回vxdataclass对象

        Arguments:
            table_name {str} -- 数据表格名称

        Returns:
            vxDataClass -- 返回vxdataclass对象
        """
        sql = f"""SELECT * FROM `{table_name}`"""
        query_conditions = list(conditions)
        _, vxdatacls = self._tblmapping[table_name]
        if query:
            query_conditions.extend(
                [f"{key}='{value or ''}'" for key, value in query.items()]
            )
        if query_conditions:
            sql += f""" WHERE {' and '.join(query_conditions)}"""
        sql += ";"

        obj = self.execute(sql).fetchone()
        return vxdatacls(**obj) if obj else None

    def insert(self, table_name: str, vxdataobj: vxDataClass) -> None:
        """插入数据vxdataclass object

        Arguments:
            table_name {str} -- 数据表格名称
            vxdataobj [vxDataClass] -- 被插入对象

        """
        primary_keys, vxdatacls = self._tblmapping[table_name]
        if not isinstance(vxdataobj, (vxDataClass, vxdatacls)):
            raise TypeError(f"vxdataobj 类型{type(vxdataobj)}非{vxdatacls.__name__}")

        col_names = []
        values = []
        update_string = []

        for col, value in vxdataobj.items():
            col_names.append(f"'{col}'")
            if value is None:
                value = ""
            elif value is False:
                value = 0
            elif value is True:
                value = 1
            elif isinstance(value, Enum):
                value = value.name

            values.append(f"'{value}'")
            if col not in primary_keys:
                update_string.append(f"{col}=excluded.{col}")

            sql = f"""INSERT INTO {table_name} 
                    ({','.join(col_names)}) \n\tVALUES ({','.join(values)})"""
        with self:
            self.execute(sql)

    def remove(self, table_name: str, *vxdataobjs) -> None:
        """删除vxdataclass对象

        Arguments:
            table_name {str} -- 数据表格名称
        """
        primary_keys, vxdatacls = self._tblmapping[table_name]
        if not primary_keys:
            primary_keys = vxdatacls.__vxfields__
            primary_keys.pop("created_dt")
            primary_keys.pop("updated_dt")

        datas = []
        query_str = " and ".join([f"{key} =:{key}" for key in primary_keys])
        for vxdataobj in vxdataobjs:
            data = {}
            for key in primary_keys:
                value = getattr(vxdataobj, key)
                if value is None:
                    value = ""
                elif value is False:
                    value = 0
                elif value is True:
                    value = 1
                elif isinstance(value, Enum):
                    value = value.name
                data[key] = value
            datas.append(data)

        sql = f"DELETE FROM `{table_name}` WHERE {query_str}"

        with self:
            self.executemany(sql, datas)

    def delete(self, table_name: str, *conditions, **query) -> None:
        """删除符合条件的数据

        Arguments:
            table_name {str} -- 数据表格名称
        """
        sql = f"""DELETE FROM `{table_name}`"""
        query_conditions = list(conditions)

        if query:
            query_conditions.extend(
                [f"{key}='{value or ''}'" for key, value in query.items()]
            )
        if query_conditions:
            sql += f""" WHERE {' and '.join(query_conditions)}"""
        sql += ";"

        with self:
            self.execute(sql)

    def truncate(self, table_name: str) -> None:
        """清空数据表格

        Arguments:
            table_name {str} -- 数据表格名称

        """
        return self.delete(table_name)

    def count(self, table_name: str, *conditions, **query) -> int:
        """返回数据表格中的数据条数

        Arguments:
            table_name {str} -- 数据表格名称
            conditions {List[str]} -- 查询条件
            query {Dict[str,str]} -- 查询条件

        Returns:
            int -- 返回数据条数

        """
        sql = f"""SELECT COUNT(1) AS cnt FROM `{table_name}`"""
        query_conditions = list(conditions)

        if query:
            query_conditions.extend(
                [f"{key}='{value or ''}'" for key, value in query.items()]
            )
        if query_conditions:
            sql += f""" WHERE {' and '.join(query_conditions)}"""
        sql += ";"
        return self.execute(sql).fetchone()["cnt"]

    def max(self, table_name: str, col: str, *conditions, **query) -> Union[int, float]:
        sql = f"""SELECT MAX(`{col}`) AS col_max FROM `{table_name}`"""
        query_conditions = list(conditions)

        if query:
            query_conditions.extend(
                [f"{key}='{value or ''}'" for key, value in query.items()]
            )
        if query_conditions:
            sql += f""" WHERE {' and '.join(query_conditions)}"""
        sql += ";"
        return self.execute(sql).fetchone()["col_max"]

    def min(self, table_name: str, col: str, *conditions, **query) -> Union[int, float]:
        sql = f"""SELECT MIN('{col}') AS col_min FROM `{table_name}`"""
        query_conditions = list(conditions)

        if query:
            query_conditions.extend(
                [f"{key}='{value or ''}'" for key, value in query.items()]
            )
        if query_conditions:
            sql += f""" WHERE {' and '.join(query_conditions)}"""
        sql += ";"
        return self.execute(sql).fetchone()["col_min"]

    @contextmanager
    def start_session(self):
        """启动事务

        Yields:
            _type_ -- _description_
        """

        with self._lock, self:
            yield self


if __name__ == "__main__":
    from vxutils import vxtime

    class vxTest(vxDataClass):
        """初始化"""

        id: str = vxUUIDField()
        name: str = vxIntField(0)
        data: str = vxField()
        is_check: bool = vxBoolField(True)
        due_dt: float = vxDatetimeField(formatter_string="%Y-%m-%d %H:%M:%S.%f")

    testdb = vxSQLiteDB.connect()
    testdb.create_table("test", ["id"], vxTest)

    with vxtime.timeit():
        objs = [
            vxTest(
                id=i,
                name=f"clear{i}",
                is_check=False,
                due_dt="2023-03-01",
                created_dt="2023-03-01",
            )
            for i in range(10000)
        ]
        # testdb.executemany(
        #    """UPDATE test
        #    SET
        #        name=:name
        #    WHERE id=:cnt
        #    """,
        #    [
        #        {"cnt": 1, "name": "this is test1", "updated_dt": 11},
        #        {"cnt": 2, "name": "this is test2", "updated_dt": 22},
        #        {"cnt": 3, "name": "this is test3", "updated_dt": 33},
        #    ],
        # )

        testdb.save("test", objs)
    ids = testdb.distinct("test", "name")
    print(ids)
    print(testdb.max("test", "id"))
    exit(1)
    # print([tuple(item.values()) for item in cur])
    # testdb.insert("test", objs[0])

    # a = input("press any key to continue...")
    for i in testdb.find("test"):
        logger.warning(i.id)
        testdb.remove("test", i)
    cur = testdb.execute("SELECT COUNT(1) as cnt FROM test")
    print(next(cur))
    with testdb.start_session() as session:
        print(session.max("test", "id"))

    testdb.disconnect()
