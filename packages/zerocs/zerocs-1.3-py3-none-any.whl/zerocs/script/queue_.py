"""
@time 2023-4-2
@auther YanPing
"""
from ._queue import _Queue


class Queue(_Queue):

    def _get_container(self, service_name, config):
        """
        Get Rpc Container
        :param service_name: 
        :param config: 
        :return: 
        """
        return super()._get_container(service_name, config)

    def _get_container_main(self, config):
        """
        Get Rpc Container
        :param config:
        :return:
        """
        return super()._get_container_main(config)

    def _get_container_main_config(self, config):
        """
        Get Rpc Container
        :param config:
        :return:
        """
        return super()._get_container_main_config(config)
