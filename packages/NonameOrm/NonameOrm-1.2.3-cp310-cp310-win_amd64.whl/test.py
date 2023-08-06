import threading

from NonameOrm.Model.DataModel import DataModel, get_executor
from NonameOrm.Model.ModelProperty import *

from enum import Enum

from NonameOrm.Model.ModelProperty import auto_increment


class Sku(DataModel):
    id: int = IntProperty(default=auto_increment, pk=True, Null=False)
    sku_id: str = StrProperty(typeArgs=(128,), Null=False)
    seq: int = IntProperty(typeArgs=(2,))


class WatchSku(DataModel):
    id: Union[int, IntProperty] = IntProperty(Null=False, pk=True)
    sku_id: str = StrProperty(typeArgs=(128,), Null=False)


class TaskState(Enum):
    enable = 'enable'
    disable = 'disable'


class Task(DataModel):
    id: int = IntProperty(default=auto_increment, pk=True, Null=False)
    product_id = StrProperty(typeArgs=(128,), Null=False)
    name = StrProperty(typeArgs=(128,))
    task_state: TaskState = StrProperty(typeArgs=(16,), Null=False, default=TaskState.disable.value)
    watch_sku_list = ForeignKey(WatchSku, Type=ForeignType.MANY_TO_MANY, targetBindCol=WatchSku.id)
    product_sku_list = ForeignKey(Sku, Type=ForeignType.MANY_TO_MANY)


class ActiveProduct(DataModel):
    id: int = IntProperty(default=auto_increment, pk=True, Null=False)
    product_id = StrProperty(typeArgs=(128,), Null=False)
    created_time = TimestampProperty(default=current_timestamp)


if __name__ == '__main__':
    from NonameOrm.DB.Connector import Sqlite3Connector
    from NonameOrm.DB.DB import DB

    DB.create(connector=Sqlite3Connector(path=":memory:")).GenerateTable()


    def save():
        get_executor(Task).save(Task(product_id="123", name="test", task_state=TaskState.enable.value))

    threads = []

    for i in range(1000):
        t = threading.Thread(target=save)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
