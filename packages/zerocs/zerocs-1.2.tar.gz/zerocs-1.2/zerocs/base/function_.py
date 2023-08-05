"""
@time 2023-4-2
@auther YanPing
"""
from ._function import _Function


class Function(_Function):

    def _set_function(self, func_name, value):
        """
         Set function for the current class, type dict
        :param func_name: function name
        :param value: function obj
        :return:
        """
        super()._set_function(func_name, value)

    def _set_cls_function(self, cls, func_name, value):
        """
        Add a method to the specified class
        :param cls: cls obj
        :param func_name: function name
        :param value: function obj
        :return:
        """
        super()._set_cls_function(cls, func_name, value)
