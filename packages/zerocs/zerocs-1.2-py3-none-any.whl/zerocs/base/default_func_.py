"""
@time 2023-4-2
@auther YanPing
"""
from ._default_func import _ServiceRegister, _ZeroFWService, _ZeroFWConfig


class ServiceRegister(_ServiceRegister):

    def _service_register(self, cls, master=False):
        """
        The service class object to register
        :param cls: class
        :return:
        """
        super()._service_register(cls, master)


class ZeroFWService(_ZeroFWService):
    """
    zerocs config service
    """


class ZeroFWConfig(_ZeroFWConfig):
    """
    zerocs config service
    """
