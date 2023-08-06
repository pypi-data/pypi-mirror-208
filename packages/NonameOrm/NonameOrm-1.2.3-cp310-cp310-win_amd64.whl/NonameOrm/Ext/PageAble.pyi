from typing import List, Optional, TypedDict, Union, Awaitable, Self, Callable, Type, Any, TypeVar, Generic

from NonameOrm.DB.Generator import SqlGenerator
from NonameOrm.Model.DataModel import DataModel, ModelInstance
from NonameOrm.Model.ModelProperty import FilterListCell

from NonameOrm.Ext.Dict import DictPlus



T = TypeVar('T')
from NonameOrm.Ext import Page




class _PageAble(Generic[T]):
    """
    分页控制器

    本类支持链式调用
    """

    def __init__(self, target: T, page: Optional[int] = 1, pageSize: Optional[int] = 10, findForeign: Optional[bool] = False):
        """

        :param target:
        :param page:
        :param findForeign:
        :param pageSize:
        """
        pass

    def filter(self, args: Optional[FilterListCell] = None) -> Union["_PageAble"[T], Self[T]]:
        """
        设置过滤条件

        :param args: FilterListCell
        :return: PageAble
        """
        pass

    def findForeign(self) -> 'PageAble':
        pass

    def orderBy(self, *order: List[str]) -> 'PageAble':
        pass

    def setPage(self, page: int, pageSize: Optional[int] = 0) -> Self:
        """
        设置分页

        :param page: 当前页数
        :param pageSize: 页面大小 默认可不传
        :return: PageAble
        """
        pass

    def editSql(self, callable: Callable[[SqlGenerator], None]) -> Self: ...

    @property
    def sql(self) -> SqlGenerator: ...

    def execute(self) -> Union[Page[T], Awaitable[Page[T]]]:
        """
        链式调用尽头
        正式进行数据获取
        """
        pass

def PageAble(target: T, page: int = 1, pageSize: int = 10, findForeign: bool = False) -> _PageAble[T]: ...
