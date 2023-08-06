"""
@time 2023-4-2
@auther YanPing
"""
import time
from zerocs.mate import _Mate


class _Base(_Mate):

    def _set(self, attr_name, value):
        setattr(self, attr_name, value)

    def _get_dict(self):
        return self.__dict__

    def _get_class_dict(self, ):
        return self.__class__.__dict__

    def _call_sub_function(self, name):
        func = getattr(self, name)
        return func

    def _get_attr(self, attr_name):
        return self._get_dict().get(attr_name)

    def _set_str(self, attr_name, value):
        if type(attr_name) == str and type(value) == str:
            self._set(attr_name, value)
        else:
            raise 'type error: is not str'

    def _set_int(self, attr_name, value):
        if type(attr_name) == str and type(value) == int:
            self._set(attr_name, value)
        else:
            raise 'type error: is not int'

    def _set_list(self, attr_name, value):
        if type(attr_name) == str and type(value) == list:
            self._set(attr_name, value)
        else:
            raise 'type error: is not list'

    def _set_dict(self, attr_name, value):
        if type(attr_name) == str and type(value) == dict:
            self._set(attr_name, value)
        else:
            raise 'type error: is not dict'

    def _list_append(self, attr_name, value):
        dct = self._get_attr(attr_name)
        if dct is None:
            self._set_list(attr_name, [value])
        else:
            dct.append(value)

    def _get_timestamp_millimeter(self):
        timestamp = int(round(time.time() * 1000))
        return timestamp

    def _get_timestamp_next_second(self, last_timestamp):
        timestamp = self._get_timestamp_millimeter()
        while timestamp <= last_timestamp:
            timestamp = self._get_timestamp_millimeter()
        return timestamp
