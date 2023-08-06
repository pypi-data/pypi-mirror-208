from NonameOrm.Model.ModelExcutor cimport AsyncModelExecutor,BaseModelExecutor
from NonameOrm.Model.ModelProperty cimport FilterListCell

from NonameOrm.Ext.Dict cimport DictPlus

cdef class _Page(DictPlus):
    pass

cdef class _PageAble:
    cdef:
        object target
        BaseModelExecutor executor
        FilterListCell filter
        int page, pageSize
        bint deep

    cpdef object _execute(self)