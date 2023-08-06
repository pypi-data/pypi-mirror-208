"""数据库ORM抽象"""

from abc import ABC, abstractmethod
import contextlib
from typing import Iterator, List, Optional, Type, Union
from multiprocessing import Lock
from vxutils.dataclass import vxDataClass


class vxDataBase(ABC):
    """基于vxDataClass 数据管理"""

    def __init__(self, dbconn=None, db_uri: str = None) -> None:
        self._dbconn = dbconn
        self._tblmapping = {}
        self._lock = Lock()

    @classmethod
    def connect(cls, db_uri: str = None, **kwargs) -> "vxDataBase":
        """连接数据库"""
        raise NotImplementedError

    def disconnect(self):
        """断开连接数据库"""
        raise NotImplementedError

    @property
    def lock(self):
        """数据锁"""
        return self._lock

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

    def findone(self, table_name: str, *conditions, **query) -> Optional[vxDataClass]:
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

    def insert(self, table_name: str, vxdataobj: vxDataClass) -> None:
        """插入数据vxdataclass object

        Arguments:
            table_name {str} -- 数据表格名称
            vxdataobj [vxDataClass] -- 被插入对象

        Raises:
            Valueerror -- 若插入对象以存在数据库时，抛出异常
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

    # def get_connection(self) -> None:
    #    """数据库连接"""

    def count(self, table_name: str, *conditions, **query) -> int:
        """返回数据表格中的数据条数

        Arguments:
            table_name {str} -- 数据表格名称
            conditions {List[str]} -- 查询条件
            query {Dict[str,str]} -- 查询条件

        Returns:
            int -- 返回数据条数
        """

    def max(self, table_name: str, col: str, *conditions, **query) -> Union[int, float]:
        """获取数据表格中的最大值

        Arguments:
            table_name {str} -- 数据表格名称
            col {str} -- 字段名称
            conditions {List[str]} -- 查询条件
            query {Dict[str,str]} -- 查询条件
        Returns:
            Union[int, float] -- 最大值
        """

    def min(self, table_name: str, col: str, *conditions, **query) -> Union[int, float]:
        """获取数据表格中的最小值

        Arguments:
            table_name {str} -- 数据表格名称
            col {str} -- 字段名称
            conditions {List[str]} -- 查询条件
            query {Dict[str,str]} -- 查询条件
        Returns:
            Union[int, float] -- 最小值
        """

    @contextlib.contextmanager
    def start_session(self):
        """开始session，锁定python线程加锁，保障一致性"""
