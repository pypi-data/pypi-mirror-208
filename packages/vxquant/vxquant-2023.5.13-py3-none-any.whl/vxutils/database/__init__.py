"""数据库ORM抽象"""

from abc import ABC, abstractmethod
import contextlib
from typing import Iterator, List, Optional, Type
from multiprocessing import Lock
from vxutils.dataclass import vxDataClass
from vxutils.database.mongodb import vxMongoDB
from vxutils.database.base import vxDataBase

__all__ = ["vxDataBase", "vxDBTable", "vxMongoDB"]


class vxDataBase1(ABC):
    """基于vxDataClass 数据管理"""

    def __init__(self, dbconn) -> None:
        self._dbconn = dbconn
        self._tblmapping = {}
        self._lock = Lock()

    @classmethod
    def connect(cls, **kwargs) -> "vxDataBase":
        """连接数据库"""
        raise NotImplementedError

    def disconnect(self):
        """断开连接数据库"""
        raise NotImplementedError

    def __getitem__(self, table_name: str) -> "vxDBTable":
        return self.__dict__[table_name]

    @abstractmethod
    def create_table(
        self,
        table_name: str,
        primary_keys: List[str],
        vxdatacls: Type[vxDataClass],
        if_exists: str = "ignore",
    ) -> "vxDataBase":
        """创建数据表

        Arguments:
            table_name {str} -- 数据表名称
            primary_keys {List[str]} -- 表格主键
            vxdatacls {_type_} -- 表格数据格式
            if_exists {str} -- 如果table已经存在，若参数为ignore ，则忽略；若参数为 drop，则drop掉已经存在的表格，然后再重新创建

        Returns:
            vxDataBase -- 返回数据表格实例
        """

    @abstractmethod
    def drop_table(self, table_name: str) -> None:
        """删除数据表

        Arguments:
            table_name {str} -- 数据表名称
        """

    def save(self, table_name: str, *vxdataobj) -> None:
        """保存vxdataclass的objects

        Arguments:
            table_name {str} -- 数据表名称
            vxdataobj [vxdataobj] -- 需要保存的vxdataclass objects
        """

    def find(self, table_name: str, *conditions, **query) -> Iterator:
        """查询数据

        Arguments:
            table_name {str} -- 数据表名称
            conditions [list[str]] -- 查询条件
            query {str} -- 查询条件
        """

    def remove(self, table_name: str, *vxdataobjs) -> None:
        """删除数据vxdataclass objects

        Arguments:
            table_name {str} -- 数据表名称
            vxdataobjs {vxdatacls_obj} -- 待删除的objects

        """

    def delete(self, table_name: str, *conditions, **query) -> None:
        """批量删除

        Arguments:
            table_name {str} -- 数据表名称
            conditions [list(str)] -- 查询条件
            query {str} -- 查询条件
        """

    def truncate(self, table_name: str) -> None:
        """清空表格

        Arguments:
            table_name {str} -- 待清空的表格名称
        """

    def distinct(self, table_name: str, col: str, *conditions, **query) -> List:
        """去重

        Arguments:
            table_name {str} -- 数据表格名称
            col {str} -- 字段名称
            conditions / query -- 查询条件

        Returns:
            List -- _description_
        """

    @abstractmethod
    def get_connection(self) -> None:
        """数据库连接"""

    @contextlib.contextmanager
    def start_session(self):
        """开始session，锁定python线程加锁，保障一致性"""


class vxDBTable(ABC):
    """数据表映射"""

    def __init__(
        self,
        table_name: str,
        primary_keys: List[str],
        datacls: Type[vxDataClass],
        db: vxDataBase,
    ) -> None:
        """数据表映射

        Arguments:
            table_name: {str} -- 数据表名称
            primary_keys {List[str]} -- 主键
            dataclass {Type[vxDataClass]} -- 对应
        """
        self._table_name = table_name
        self._primary_keys = primary_keys
        self._datacls = datacls
        self._db = db

    @abstractmethod
    def save(self, obj: vxDataClass) -> None:
        """保存vxdata obj对象

        Arguments:
            obj {vxDataClass} -- vxdata obj对象
        """

    @abstractmethod
    def savemany(self, *objs: List[vxDataClass]) -> None:
        """同时保存多个obj对象

        Arguments:
            objs {List[vxDataClass]} -- 多个obj对象
        """

    @abstractmethod
    def find(self, query) -> Iterator:
        """查询vxdata obj对象

        Arguments:
            conditions {List[str]} -- 查询条件,如: "id=3","age>=5"...

        Yields:
            Iterator -- vxdata obj迭代器
        """

    @abstractmethod
    def delete(self, obj: Optional[vxDataClass]) -> None:
        """删除vxdata obj对象

        Arguments:
            obj {vxDataClass} -- obj

        Raises:
            ValueError -- 若 obj 类型不是table对应的dataclass，则抛出 ValueError

        """

    def deletemany(self, query) -> None:
        """按条件删除vxdata obj对象

        Arguments:
            conditions {List[str]} -- 查询条件,如: "id=3","age>=5"...

        Raises:
            ValueError -- 若 conditions 为空，则抛出异常。希望清空表格时，适用 truncate()接口

        """

    @abstractmethod
    def distinct(self, col_name: str, query=None) -> List:
        """去重后的数值列表

        Arguments:
            col_name {str} -- 去重后列表名称

        Returns:
            List -- 去重后的数值列表
        """

    @abstractmethod
    def truncate(self) -> None:
        """清空数据表"""

    @abstractmethod
    def create_table(self) -> None:
        """创建数据库表"""

    @abstractmethod
    def drop_table(self) -> None:
        """删除数据库表"""
