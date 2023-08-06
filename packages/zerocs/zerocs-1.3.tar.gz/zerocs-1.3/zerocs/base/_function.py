"""
@time 2023-4-2
@auther YanPing
"""

from zerocs.mate import _Mate


class _Function(_Mate):

    def _set_function(self, func_name, value):
        if type(func_name) == str:
            self._set(func_name, value)
        else:
            raise 'type error: function name is not str'

    def _set_cls_function(self, cls, func_name, value):
        if type(func_name) == str:
            setattr(cls, func_name, value)
        else:
            raise 'type error: function name is not str'
