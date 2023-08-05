"""
@time 2023-4-1
@auther yanping

"""

from ._base import _Base


class Base(_Base):

    def _set(self, attr_name, value):
        """
        Set attr for the current class
        :param attr_name: attr name
        :param value: attr value
        :return:
        """
        super()._set(attr_name, value)

    def _get_dict(self):
        """
        get __dict__ for the current class
        :return:
        """
        return super()._get_dict()

    def _get_class_dict(self):
        """
        get __class__.__dict__ for the current class
        :return:
        """
        return super()._get_class_dict()

    def _call_sub_function(self, name):
        """
        Calling a sub function method
        :param name: sub function name
        :return:
        """
        return super()._call_sub_function(name)

    def _get_attr(self, attr_name):
        """
        get attr for the current class.__dict__
        :param attr_name:
        :return:
        """
        return super()._get_attr(attr_name)

    def _set_str(self, attr_name, value):
        """
        Set attr for the current class, type str
        :param attr_name: attr name
        :param value: attr value
        :return:
        """
        super()._set_str(attr_name, value)

    def _set_int(self, attr_name, value):
        """
        Set attr for the current class, type int
        :param attr_name: attr name
        :param value: attr value
        :return:
        """
        super()._set_int(attr_name, value)

    def _set_list(self, attr_name, value):
        """
        Set attr for the current class, type list
        :param attr_name: attr name
        :param value: attr value
        :return:
        """
        super()._set_list(attr_name, value)

    def _set_dict(self, attr_name, value):
        """
        Set attr for the current class, type dict
        :param attr_name: attr name
        :param value: attr value
        :return:
        """
        super()._set_dict(attr_name, value)

    def _list_append(self, attr_name, value):
        """
        Add a value to the specified list
        :param attr_name: attr name
        :param value: attr value
        :return:
        """
        super()._list_append(attr_name, value)

    def _get_timestamp_millimeter(self):
        """
        Get millimeter timestamp
        :return:
        """
        return super()._get_timestamp_millimeter()

    def _get_timestamp_next_second(self, last_timestamp):
        """
        Get next second timestamp
        :param last_timestamp: last timestamp
        :return:
        """
        return super()._get_timestamp_next_second(last_timestamp)
